import pandas as pd
from sklearn import naive_bayes
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from joblib import dump, load 
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from app.MySQLUtility import MySQLUtility
from app.PreProcessText import PreProcessText
from app.Risk_Score_Service import Risk_Score_Service

# load the dataset
labels, texts = [], []
pre_process = PreProcessText()
risk_score = Risk_Score_Service()
dbutil = MySQLUtility()

class Keyword_Classifier:
    def __init__(self) -> None:
        pass 

    trainDF = pd.DataFrame()
    text_clf = ""

    def prepare_training_data(self):
        results = dbutil.get_seed_data()
        for row in results: 
            keywords = row['keywords']
            if (keywords != None and len(keywords)) > 0:
                labels.append(row['label'])
                texts.append(row['keywords'])
                
        # create a dataframe using texts and lables
        self.trainDF = pd.DataFrame()
        self.trainDF['text'] = texts
        self.trainDF['label'] = labels

    def train_model(self):
        self.text_clf = Pipeline([('vect', CountVectorizer(stop_words='english')),
                      ('tfidf', TfidfTransformer()),
                      ('clf', naive_bayes.MultinomialNB())])
        self.text_clf = self.text_clf.fit(self.trainDF['text'], self.trainDF['label'])

        dump(self.text_clf, './model/keyword/keyword_class.joblib')
        return 

    def evaluate_model(self):
        self.prepare_training_data()
        self.text_clf = load('./model/keyword/keyword_class.joblib')

        predicted = self.text_clf.predict(self.trainDF['text'])

        y_labels = self.trainDF['label'].to_numpy()
        report = classification_report(y_labels, predicted)
        print ("Classification Report : \n", report)
        matrix = confusion_matrix(y_labels, predicted)
        print("Confusion Matrix: \n", matrix)
        acc_score = accuracy_score(y_labels, predicted)
        print("Accuracy Score: \n", acc_score*100, "%")

    def predict_text_data(self, text):
        self.text_clf = load('./model/keyword/keyword_class.joblib')
        predictDF = pd.DataFrame()
        texts = []
        text = pre_process.preprocess_text(text)
        texts.append(text)
        predictDF['text'] = texts
        predicted = self.text_clf.predict(predictDF['text'])
        predicted_prob = self.text_clf.predict_proba(predictDF['text'])
        
        return predicted[0], max(predicted_prob[0])

    def process_contract_data(self):       
        results = dbutil.get_contracts(page="true")
        batch_insert = []    
        for row in results:
            article_text = row["content"]
            print("Filename:", row["title"])  
            sentences = pre_process.get_sentences(article_text)
            for c_sentence in sentences: 
                c_sentence = str(c_sentence)
                c_sentence = pre_process.clean_text(c_sentence)
                if len(c_sentence) > 4:                     
                    predict_label, predict_prb = self.predict_text_data(c_sentence) 
                    p_score = predict_prb * 100  
                    c_score = risk_score.calculate_score(c_sentence, p_score)
                    label = predict_label.lower().strip()

                    if p_score > 75:
                        print ("Sentences : ", c_sentence, ", Result : ", label.lower().strip(), ", Score : ", c_score) 
                        insert_json = {"content" : c_sentence, "type" : "contract", "label" : label, "eval_label" : '', "score" : c_score, "eval_score" : 0, "domain" : 'liability', "userid": "admin"}
                        batch_insert.append(insert_json)
        dbutil.save_training_data_batch(batch_insert) 
        return 

    def process_seed_data(self):       
        results = dbutil.get_training_data(type="seed")
        type = "seed"
        batch_insert = []    
        for row in results:
            article_text = row["content"]
            id = row['id']
            eval_label = row['eval_label']
            eval_score = row['eval_score']

            sentences = pre_process.get_sentences(article_text)
            for c_sentence in sentences: 
                c_sentence = str(c_sentence)
                if c_sentence != None and len(c_sentence) > 4:                     
                    predict_label, predict_prb = self.predict_text_data(c_sentence) 
                    p_score = predict_prb * 100  
                    c_score = risk_score.calculate_score(c_sentence, p_score)
                    insert_json = {"id" : id, "eval_label" : eval_label, "score" : c_score, "eval_score" : eval_score}
                    batch_insert.append(insert_json)
        dbutil.update_training_data_batch(batch_insert) 
        return 

