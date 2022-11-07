from sklearn import preprocessing
import pandas as pd
import sklearn.model_selection as model_selection
from sklearn import naive_bayes
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics

from app.BQUtility import BQUtility
from joblib import dump, load 

# load the dataset
labels, texts = [], []

class Keyword_Classifier:
    def __init__(self) -> None:
        pass 
    
    def prepare_training_data(self):
        dbutil = BQUtility()    

        results = dbutil.get_seed_data()
        for row in results: 
            if (len(row['keywords'])) > 0:
                labels.append(row['label'])
                texts.append(row['keywords'])
                
        # create a dataframe using texts and lables
        trainDF = pd.DataFrame()
        trainDF['text'] = texts
        trainDF['label'] = labels

        # split the dataset into training and validation datasets 
        train_x, valid_x, train_y, valid_y = model_selection.train_test_split(trainDF['text'], trainDF['label'])
        # label encode the target variable 
        encoder = preprocessing.LabelEncoder()
        train_y = encoder.fit_transform(train_y)
        valid_y = encoder.fit_transform(valid_y)

        # ngram level tf-idf 
        tfidf_vect_ngram = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', ngram_range=(2,3), max_features=5000)
        tfidf_vect_ngram.fit(trainDF['text'])
        xtrain_tfidf_ngram =  tfidf_vect_ngram.transform(train_x)
        xvalid_tfidf_ngram =  tfidf_vect_ngram.transform(valid_x)

        print("xtrain_tfidf_ngram: ", xtrain_tfidf_ngram)

        # Naive Bayes on Ngram Level TF IDF Vectors
        classifier = naive_bayes.MultinomialNB()
        # fit the training dataset on the classifier
        classifier.fit(xtrain_tfidf_ngram, train_y)
        
        # predict the labels on validation dataset
        predictions = classifier.predict(xvalid_tfidf_ngram)
        #predict_lable = encoder.inverse_transform(predictions)  

        accuracy = metrics.accuracy_score(predictions, valid_y)
        print ("Accuracy - N-Gram Vectors: ", accuracy)

        dump(classifier, './model/keyword/keyword_class.joblib')
        return classifier, tfidf_vect_ngram, encoder

    def predict_text_data(self, classifier, tfidf_vect_ngram, text, encoder):
        trainDF = pd.DataFrame()
        labels, texts = [], []
        texts.append(text)
        labels.append("")
        trainDF['text'] = texts
        trainDF['label'] = labels

        print ("trainDF['text'] : ", trainDF['text'])
        xtrain_tfidf_ngram =  tfidf_vect_ngram.transform(trainDF['text'])
        print ("xtrain_tfidf_ngram : ", xtrain_tfidf_ngram)

        # predict the labels on validation dataset
        try:
            predictions = classifier.predict(xtrain_tfidf_ngram)
        except ValueError:
            print("ValueError:")
        else:
            predict_prb_a = classifier.predict_proba(xtrain_tfidf_ngram)
            predict_label = encoder.inverse_transform(predictions)
            predict_prb = predict_prb_a[0][predictions[0]]

            return predict_label[0], predict_prb

    def complete_processing(self):
        classifier, tfidf_vect_ngram, encoder = self.prepare_training_data()
        
        dbutil = BQUtility()
        results = dbutil.get_contracts(page="true")
        for row in results:
            article_text = row["content"]
            for c_sentence in article_text.split('.'): 
                print("predict_text_data(): Before:")                
                predict_label, predict_prb = self.predict_text_data(classifier, tfidf_vect_ngram, c_sentence, encoder)
                print("predict_text_data : After: ", predict_label, predict_prb)
                score = predict_prb * 100  
                label = predict_label
                if score > 80:
                    print ("Sentences : ", c_sentence, "Result : ", label, "Score : ", score) 
                    dbutil.save_training_data(c_sentence, label, "generated", "")
        return 

