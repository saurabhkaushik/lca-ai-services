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
from app.Transformer_Trainer import Transformer_Trainer

model_checkpoint = "distilbert-base-uncased"
min_sentence_len = 10
processTxt = PreProcessText()
presence_thresthold = 94
model_folder_base = './model/'

class Transformer_Service(object):
    risk_score = None
    model_dict = None
    dbutil = None 
    domains = None
    model_train = None

    def __init__(self, dbutil, domains):
        self.dbutil = dbutil
        self.domains = domains
        self.risk_score = Risk_Score_Service(dbutil, domains)  
        self.model_train = Transformer_Trainer(self.dbutil)
        pass

    def train_model(self, domain):
        model_folder = model_folder_base + domain + '/'
        trainer = Transformer_Trainer(self.dbutil)
        trainer.prepare(domain)
        trainer.train(model_folder)
        return

    def preload_models(self):
        self.model_dict = {}
        for domain in self.domains:
            model_folder = model_folder_base + domain + '/'
            path_to_file = model_folder + 'config.json'
            if exists(path_to_file):
                try:
                    self.model_dict[domain] = AutoModelForSequenceClassification.from_pretrained(model_folder)
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
                results = self.model_train.predict_model(c_sentence, model)
                if results:
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
                    results = self.model_train.predict_model(c_sentence, model)
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
                results = self.model_train.predict_model(article_text, model)
                score = (results[0]["score"] * 100)
                label = results[0]["label"]
                single_d = {"id": row['id'], "score": score_2,
                            "eval_label": label, "eval_score": score}
                batchupdate.append(single_d)
        print(len(batchupdate))
        self.dbutil.update_training_data_batch(batchupdate)
        return    

    def evalute(self, domain):
        ref = []
        pred = []

        results = self.get_training_data(domain)
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