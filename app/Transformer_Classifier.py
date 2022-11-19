import re

import pandas as pd
import pyarrow as pa
from datasets import Dataset
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.model_selection import train_test_split
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          Trainer, TrainingArguments, pipeline)

from app.MySQLUtility import MySQLUtility
from app.PreProcessText import PreProcessText
from app.Risk_Score_Service import Risk_Score_Service

model_checkpoint = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

dbutil = MySQLUtility()
risk_score = Risk_Score_Service()
processTxt = PreProcessText()


class Transformer_Classifier:
    label_y = dict()
    label_x = dict()

    def __init__(self) -> None:
        pass

    def process_data(self, row):
        text = row['content']
        text = str(text)
        text = ' '.join(text.split())

        encodings = tokenizer(text, padding="max_length",
                              truncation=True, max_length=128)

        label = self.label_y[row['label'].lower().strip()]

        encodings['label'] = label
        encodings['text'] = text

        return encodings

    def prepare_train_dataset(self, domain):
        processed_data = []
        train_data = dbutil.get_training_data(domain)

        label_count = 0
        for row in train_data:
            key = row["label"].lower().strip()
            if not key in self.label_y.keys():
                self.label_y.update({key: label_count})
                self.label_x.update({label_count: key})
                label_count += 1

        train_data = dbutil.get_training_data(domain)
        for row in train_data:
            processed_data.append(self.process_data(row))

        new_df = pd.DataFrame(processed_data)

        train_df, valid_df = train_test_split(
            new_df,
            test_size=0.2,
            random_state=2022
        )

        train_hg = Dataset(pa.Table.from_pandas(train_df))
        valid_hg = Dataset(pa.Table.from_pandas(valid_df))
        return train_hg, valid_hg

    def load_model(self, domain):
        model = AutoModelForSequenceClassification.from_pretrained('./model/' + domain + '/')
        return model

    def training(self, domain):
        train_hg, valid_hg = self.prepare_train_dataset(domain)

        training_args = TrainingArguments(
            output_dir="./result", evaluation_strategy="epoch")
        id2label = self.label_x
        label2id = {val: key for key, val in id2label.items()}
        num_labels = len(id2label)

        model = AutoModelForSequenceClassification.from_pretrained(
            model_checkpoint, num_labels=num_labels, id2label=id2label, label2id=label2id)

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_hg,
            eval_dataset=valid_hg,
            tokenizer=tokenizer
        )
        trainer.train()
        metrics = trainer.evaluate()
        print("Metrics : ", metrics)
        model.save_pretrained('./model/'+ domain + '/')
        return model

    def predict(self, sentences, model):
        classifier = pipeline("text-classification",
                              model=model, tokenizer=tokenizer)
        results = classifier(sentences)
        return results

    def process_contract_request(self, article_text, model):
        return_value = {}
        sentences = processTxt.get_sentences(article_text)
        e_index = 0
        for sents in sentences:
            c_sentence = sents['sentance']
            start_i = sents['start']
            end_i = sents['end']
            if len(c_sentence) > 0 and len(c_sentence) < 512:
                results = self.predict(c_sentence, model)
                label = results[0]["label"]
                p_score = (results[0]["score"] * 100)
                s_score = risk_score.get_sentiment_score(c_sentence)
                c_score = risk_score.get_semantic_score(c_sentence)
                return_value[e_index] = {"start_index": start_i, "end_index": end_i,
                                         "p_score": p_score, "s_score": s_score, "c_score": c_score, "label": label}
                e_index += 1
        return return_value

    def process_contract_training_data_eval(self, domain):
        model = self.load_model(domain)
        results = dbutil.get_training_data(domain)
        batchupdate = []
        for row in results:
            article_text = row["content"]
            score_2 = row['score']
            if article_text != None and len(article_text) > 0 and len(article_text) < 512:
                results = self.predict(article_text, model)
                score = (results[0]["score"] * 100)
                label = results[0]["label"]
                single_d = {"id": row['id'], "score": score_2,
                            "eval_label": label, "eval_score": score}
                batchupdate.append(single_d)
        print(len(batchupdate))
        dbutil.update_training_data_batch(batchupdate)
        return

    def evalute_model(self, domain):
        ref = []
        pred = []

        results = dbutil.get_training_data(domain)
        for row in results:
            ref.append(row["label"].lower().strip())
            pred.append(row["eval_label"].lower().strip())
        #print ("Ref: ", ref)
        #print ("Pred", pred)
        report = classification_report(ref, pred)
        print("Classification Report : \n", report)
        matrix = confusion_matrix(ref, pred)
        print("Confusion Matrix: \n", matrix)
        accry_score = accuracy_score(ref, pred)
        print("Accuracy Score: \n", accry_score*100, "%")
