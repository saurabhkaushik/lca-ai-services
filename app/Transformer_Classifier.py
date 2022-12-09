import logging
from os.path import exists

import pandas as pd
import pyarrow as pa
from datasets import Dataset
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.model_selection import train_test_split
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          Trainer, TrainingArguments, pipeline)

from app.PreProcessText import PreProcessText
from app.Risk_Score_Service import Risk_Score_Service

model_checkpoint = "distilbert-base-uncased"
min_sentence_len = 10
processTxt = PreProcessText()
presence_thresthold = 94
model_folder = './model/'

class Transformer_Classifier(object):
    label_y = dict()
    label_x = dict()
    risk_score = None
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    model_dict = None
    dbutil = None 
    domains = None
    train_hg = None
    valid_hg = None
    mode = None

    def __init__(self, dbutil, domains, mode):
        self.dbutil = dbutil
        self.domains = domains
        self.mode = mode
        self.risk_score = Risk_Score_Service(dbutil, domains)  
        pass

    def process_data(self, row):
        text = row['content']
        text = str(text)
        text = ' '.join(text.split())

        encodings = self.tokenizer(text, padding="max_length",
                              truncation=True, max_length=128)

        label = self.label_y[row['label'].lower().strip()]

        encodings['label'] = label
        encodings['text'] = text

        return encodings
    
    def get_training_data(self, domain): 
        if self.mode == 'accuracy': 
            return self.dbutil.get_training_data(domain, type='seed')            
        if self.mode == 'learning':
            return self.dbutil.get_training_data(domain)

    def prepare_train_dataset(self, domain):
        processed_data = []        
        train_data = self.get_training_data(domain)

        label_count = 0
        for row in train_data:
            key = row["label"].lower().strip()
            if not key in self.label_y.keys():
                self.label_y.update({key: label_count})
                self.label_x.update({label_count: key})
                label_count += 1

        train_data = self.get_training_data(domain)
        for row in train_data:
            processed_data.append(self.process_data(row))

        new_df = pd.DataFrame(processed_data)
        if not len(new_df) > 0:
            logging.exception("Data Empty")
            return 
            
        train_df = None 
        valid_df = None
        try: 
            train_df, valid_df = train_test_split(
                new_df,
                test_size=0.2,
                random_state=2022
            )
        except Exception as e: 
            logging.exception("Data Empty")
            return

        self.train_hg = Dataset(pa.Table.from_pandas(train_df))
        self.valid_hg = Dataset(pa.Table.from_pandas(valid_df))
        return 

    def preload_models(self):
        self.model_dict = {}
        for domain in self.domains:
            path_to_file = model_folder + domain + '/config.json'
            if exists(path_to_file):
                try:
                    self.model_dict[domain] = AutoModelForSequenceClassification.from_pretrained(
                        model_folder + domain + '/')
                except Exception as e: 
                    logging.exception('Could not load AI Models')
        return 

    def load_model(self, domain):
        if not self.model_dict:
            self.preload_models()
        model = None
        try:
            model = self.model_dict[domain]
        except Exception as e:
            return None
        return model

    def training(self, domain):
        if self.train_hg == None:
            logging.error('Data is empty')
            return
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
            train_dataset=self.train_hg,
            eval_dataset=self.valid_hg,
            tokenizer=self.tokenizer
        )
        trainer.train()
        metrics = trainer.evaluate()
        print("Metrics : ", metrics)
        model.save_pretrained(model_folder + domain + '/')
        return model

    def predict(self, sentences, model):
        classifier = None
        try: 
            classifier = pipeline("text-classification",
                                model=model, tokenizer=self.tokenizer)
        except Exception as e:
            logging.exception('Model missing :' + str(model))
            return None
        results = classifier(sentences)
        return results

    def evalute(self, domain, mode='training_seed'):
        ref = []
        pred = []

        results = self.get_training_data(domain, mode)
        for row in results:
            ref.append(row["label"].lower().strip())
            pred.append(row["eval_label"].lower().strip())
        try:
            report = classification_report(ref, pred)
            print("Classification Report : \n", report)
            matrix = confusion_matrix(ref, pred)
            print("Confusion Matrix: \n", matrix)
            accry_score = accuracy_score(ref, pred)
            print("Accuracy Score: \n", accry_score*100, "%")
        except:
            print()

    def process_contract_request(self, article_text, domain):
        model = self.load_model(domain)
        if model == None:
            logging.error('Model is missing')
            return
        return_value = {}
        sentences = processTxt.get_sentences(article_text)
        self.risk_score.load_polarity_data()
        e_index = 0
        for sents in sentences:
            c_sentence = sents['sentance']
            if len(c_sentence) > min_sentence_len and len(c_sentence) < 512:
                results = self.predict(c_sentence, model)
                label = results[0]["label"]
                p_score = int (results[0]["score"] * 100)
                c_score = (self.risk_score.get_context_score(c_sentence, domain))                
                risk_score = int ((p_score + c_score) / 2)
                return_value[e_index] = {"sentence" : c_sentence, 
                                         "presence_score": p_score, "context_score": c_score, "risk_score": risk_score, "label": label}
                e_index += 1
        return return_value    

    def process_contract_data(self, domain):
        model = self.load_model(domain)
        results = self.dbutil.get_contracts(domain, page="true")        
        for row in results:
            batch_insert = []
            article_text = row["content"]
            print("Filename:", row["title"])            
            sentences = processTxt.get_sentences(article_text)            
            for c_sentence in sentences:
                c_sentence = str(c_sentence['sentance'])
                if len(c_sentence) > min_sentence_len and len(c_sentence) < 512:
                    results = self.predict(c_sentence, model)
                    p_score = (results[0]["score"] * 100)
                    label = results[0]["label"]

                    if p_score > presence_thresthold:
                        print("Sentences : ", c_sentence, ", Result : ",
                              label.lower().strip(), ", P_Score : ", p_score)
                        insert_json = {"content": c_sentence, "type": "contract", "label": label, "eval_label": '',
                                       "score": p_score, "eval_score": 0, "domain": domain, "userid": "admin"}
                        batch_insert.append(insert_json)
            print ('DB Routine:')
            self.dbutil.save_training_data_batch(batch_insert)
        return
    
    def process_contract_training_data_eval(self, domain):
        model = self.load_model(domain)
        results = self.dbutil.get_training_data(domain)
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
        self.dbutil.update_training_data_batch(batchupdate)
        return    