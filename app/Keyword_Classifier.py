import logging
import traceback

import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer
from joblib import dump, load
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from app.common.MySQLUtility import MySQLUtility
from app.PreProcessText import PreProcessText

# load the dataset
pre_process = PreProcessText()
min_sentence_len = 10
keyword_threshold = 80
model_folder = './model/keyword/'

class Keyword_Classifier:
    dbutil = None 
    def __init__(self, dbutil):
        self.dbutil = dbutil
        pass

    trainDF = pd.DataFrame()
    text_clf = ""

    def prepare_training_data(self, domain):
        labels, texts = [], []
        results = self.dbutil.get_seed_data(domain)
        for row in results:
            keywords = row['keywords']
            #keywords = row['content']
            #keywords = pre_process.preprocess_text(keywords)
            if (keywords != None and len(keywords)) > 5:
                labels.append(row['label'])
                texts.append(keywords)

        # create a dataframe using texts and lables
        self.trainDF = pd.DataFrame()
        self.trainDF['text'] = texts
        self.trainDF['label'] = labels
        print (self.trainDF['label'])

    def training(self, domain):
        #print (self.trainDF['text'], self.trainDF['label'])
        self.text_clf = Pipeline([('vect', TfidfVectorizer(stop_words='english')),
                                  ('tfidf', TfidfTransformer()),
                                  ('clf', SGDClassifier(loss="modified_huber"))])
        try: 
            self.text_clf = self.text_clf.fit(
                self.trainDF['text'], self.trainDF['label'])
        except Exception as e: 
            logging.error(traceback.format_exc())
            return

        dump(self.text_clf, model_folder + domain + '/keyword_class.joblib')
        #print (self.trainDF['label'])
        return

    def evaluate_model(self, domain):
        self.prepare_training_data(domain)
        self.text_clf = load(model_folder + domain + '/keyword_class.joblib')
        predicted = None
        try:
            predicted = self.text_clf.predict(self.trainDF['text'])
        except Exception as e: 
            logging.error(traceback.format_exc())
            return

        y_labels = self.trainDF['label'].to_numpy()
        #print ('Labels', y_labels)
        #print ('Predicted', predicted)
        try:
            report = classification_report(y_labels, predicted)
            print("Classification Report : \n", report)
            matrix = confusion_matrix(y_labels, predicted)
            print("Confusion Matrix: \n", matrix)
            acc_score = accuracy_score(y_labels, predicted)
            print("Accuracy Score: \n", acc_score*100, "%")
        except Exception as e: 
            logging.error(traceback.format_exc())
            return
        return

    def predict_text_data(self, text, domain):
        self.text_clf = load(model_folder + domain + '/keyword_class.joblib')
        predictDF = pd.DataFrame()
        texts = []
        text = pre_process.preprocess_text(text)
        texts.append(text)
        predictDF['text'] = texts
        predicted = self.text_clf.predict(predictDF['text'])
        predicted_prob = self.text_clf.predict_proba(predictDF['text'])

        return predicted[0], max(predicted_prob[0])

    def process_contract_data(self, domain):
        results = self.dbutil.get_contracts(domain, page="true")
        batch_insert = []
        for row in results:
            article_text = row["content"]
            print("Filename:", row["title"])            
            sentences = pre_process.get_sentences(article_text)            
            for c_sentence in sentences:
                c_sentence = str(c_sentence['sentance'])
                if len(c_sentence) > min_sentence_len:
                    predict_label, predict_prb = self.predict_text_data(
                        c_sentence, domain)
                    p_score = predict_prb * 100
                    #s_score = risk_score.get_sentiment_score(c_sentence)
                    label = predict_label.lower().strip()

                    if p_score > keyword_threshold:
                        print("Sentences : ", c_sentence, ", Result : ",
                              label.lower().strip(), ", P_Score : ", p_score)
                        insert_json = {"content": c_sentence, "type": "contract", "label": label, "eval_label": '',
                                       "score": p_score, "eval_score": 0, "domain": domain, "userid": "admin"}
                        batch_insert.append(insert_json)
            self.dbutil.save_training_data_batch(batch_insert)
        return

''' 
    def process_seed_data(self, domain):
        results = self.dbutil.get_training_data(domain, type="seed")
        type = "seed"
        batch_insert = []
        for row in results:
            article_text = row["content"]
            id = row['id']
            eval_label = row['eval_label']
            eval_score = row['eval_score']

            sentences = pre_process.get_sentences(article_text)
            for c_sentence in sentences:
                c_sentence = str(c_sentence['sentance'])
                if c_sentence != None and len(c_sentence) > 10:
                    predict_label, predict_prb = self.predict_text_data(
                        c_sentence)
                    p_score = predict_prb * 100
                    c_score = self.risk_score.calculate_score(c_sentence, p_score)
                    insert_json = {"id": id, "eval_label": eval_label,
                                   "score": c_score, "eval_score": eval_score}
                    batch_insert.append(insert_json)
        self.dbutil.update_training_data_batch(batch_insert)
        return
'''

