import pandas as pd
from sklearn import naive_bayes
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from app.BQUtility import BQUtility
from app.PreProcessText import PreProcessText
from joblib import dump, load 
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# load the dataset
labels, texts = [], []
processTxt = PreProcessText()

class Keyword_Classifier:
    def __init__(self) -> None:
        pass 

    trainDF = pd.DataFrame()
    text_clf = ""

    def prepare_training_data(self):
        dbutil = BQUtility()    

        results = dbutil.get_seed_data()
        for row in results: 
            if (len(row['keywords'])) > 0:
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
        texts.append(text)
        predictDF['text'] = texts
        predicted = self.text_clf.predict(predictDF['text'])
        predicted_prob = self.text_clf.predict_proba(predictDF['text'])
        
        return predicted[0], max(predicted_prob[0])

    def process_contract_data(self):       
        dbutil = BQUtility()
        results = dbutil.get_contracts(page="true")
        for row in results:
            article_text = row["content"]
            print("Filename:", row["title"])  
            sentences = processTxt.get_sentences(article_text)
            #sentences = re.split(r' *[\.\?!][\'"\)\]]* *', article_text)             
            for c_sentence in sentences: 
                c_sentence = str(c_sentence)
                if len(c_sentence) > 4:                     
                    predict_label, predict_prb = self.predict_text_data(c_sentence) 
                    score = predict_prb * 100  
                    label = predict_label

                    if score > 75:
                        print ("Sentences : ", c_sentence, ", Result : ", label.lower().strip(), ", Score : ", score) 
                        dbutil.save_training_data(c_sentence, label.lower().strip(), "generated", "")
        return 

