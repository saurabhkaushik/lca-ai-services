from transformers import AutoModelForSequenceClassification
import json 
from transformers import AutoTokenizer
from transformers import pipeline
from sklearn.model_selection import train_test_split
import pandas as pd
import pyarrow as pa
from datasets import Dataset
from sklearn import preprocessing
from transformers import TrainingArguments, Trainer
import re
from app.BQUtility import BQUtility
import evaluate
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

from app.highlight_service import highlight_service

model_checkpoint = "distilbert-base-uncased"

class classify_service:

    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    high_service = highlight_service()
    dbutil = BQUtility()

    label_y = dict()
    label_x = dict()

    def __init__(self) -> None:
        pass

    def process_data(self, row):
        text = row['content']
        text = str(text)
        text = ' '.join(text.split())

        encodings = self.tokenizer(text, padding="max_length", truncation=True, max_length=128)

        label = self.label_y[row['label'].lower().strip()]

        encodings['label'] = label
        encodings['text'] = text

        return encodings

    def prepare_train_dataset(self): 
        processed_data = []    
        train_data = self.dbutil.get_training_data()
        
        label_count = 0
        for row in train_data:        
            key = row["label"].lower().strip()
            if not key in self.label_y.keys():
                self.label_y.update({key : label_count})
                self.label_x.update({label_count : key})
                label_count += 1
        
        train_data = self.dbutil.get_training_data()
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

    def training(self, train_hg, valid_hg):
        training_args = TrainingArguments(output_dir="./result", evaluation_strategy="epoch")
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
            tokenizer=self.tokenizer
        )
        trainer.train()
        metrics = trainer.evaluate()
        print ("Metrics : ", metrics)
        model.save_pretrained('./model/')
        return model

    def predict(self, sentences, model): 
        # model = AutoModelForSequenceClassification.from_pretrained('./model/')
        classifier = pipeline("text-classification", model=model, tokenizer=self.tokenizer)
        results = classifier(sentences)
        return results 

    def process_contract(self, article_text):
        model = AutoModelForSequenceClassification.from_pretrained('./model/')
        return_value = {}
        for c_sentence in article_text.split('.'):
            results = self.predict(c_sentence, model)
            score = (results[0]["score"]  * 100)
            try: 
                res = re.search(c_sentence, article_text) # TODO Revisite 
                if res:
                    stmt_index = str(res.start()) + "-" + str(res.end())
                    relevence = score
                    return_value[stmt_index] = {"start_index" : res.start(), "end_index" : res.end(), "relevence" : relevence}
            except IndexError:
                print()

        return return_value

    def contract_training_data(self):
        model = AutoModelForSequenceClassification.from_pretrained('./model/')
        dbutil = BQUtility()
        results = dbutil.get_contracts()
        for row in results:
            article_text = row["content"]
            for c_sentence in article_text.split('.'):
                try: 
                    results = self.predict(c_sentence, model)
                except RuntimeError:
                    print ("Tensor size issues.")
                else: 
                    score = (results[0]["score"]  * 100)   
                    label = results[0]["label"]
                    print ("Sentences : ", c_sentence, "Result : ", label, "Score : ", score) 
                    if score > 7:
                        print("Saved")                      
                        dbutil.save_training_data(c_sentence, label, "generated", "")
        return 
    
    def evaluate_contract_training_data(self):
        model = AutoModelForSequenceClassification.from_pretrained('./model/')
        dbutil = BQUtility()
        results = self.dbutil.get_training_data()
        for row in results:
            article_text = row["content"]
            results = self.predict(article_text, model)
            score = (results[0]["score"]  * 100) 
            label = results[0]["label"] 
            dbutil.update_training_data(row['id'], label)

        return 

    def evalute_results(self):
        ref = []
        pred = []

        results = self.dbutil.get_training_data()
        for row in results:
            ref.append(row["label"])
            pred.append(row["eval_label"])
            
        report = classification_report(ref, pred)
        print ("Classification Report : \n", report)
        matrix = confusion_matrix(ref, pred)
        print("Confusion Matrix: \n", matrix)
        accry_score = accuracy_score(ref, pred)
        print("Accuracy Score: \n", accry_score*100, "%")

'''
        accuracy = evaluate.load("accuracy")
        accuracy.add(references= ref, predictions=pred)
        acc_result = accuracy.compute()
        print ("Accuracy : ", acc_result)

        clf_metrics = evaluate.combine(["accuracy", "f1", "precision", "recall"])
        clf_results = clf_metrics.compute(references= ref, predictions=pred)
        print ("CLF Results : ", clf_results)
'''