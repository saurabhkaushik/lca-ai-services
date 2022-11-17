from app.MySQLUtility import MySQLUtility
import spacy 
from nltk.stem import WordNetLemmatizer
  
lemmatizer = WordNetLemmatizer()
nlp = spacy.load('en_core_web_sm')
dbutil = MySQLUtility()
from transformers import pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model = "distilbert-base-uncased-finetuned-sst-2-english")

class Risk_Score_Service:

    def __init__(self) -> None:
        pass

    def highlight_ranking(self, return_value):
        for r_key in return_value:
            score = return_value[r_key]['score'] 
            if score > 30: 
                return_value[r_key]["relevence_degree"] = "HIGH"
            else: 
                if score >= -30 and score <= 30: 
                    return_value[r_key]["relevence_degree"] = "MEDIUM"
                else:
                    if score < -30: 
                        return_value[r_key]["relevence_degree"] = "LOW"
        return return_value

    def calculate_score(self, sentence, score):
        data = [sentence] 
        sent_result = sentiment_pipeline(data)
        #print (sent_result)
        sent_score = (sent_result[0]['score']) if sent_result[0]['label'] == 'POSITIVE' else -(sent_result[0]['score'])
        sent_score = sent_score * 100
        adj_score = (sent_score * score) / 100
        #print(' Original Score: ', score, ' Sentiment Score: ', sent_score >> ' Adjusted Score: ', adj_score)
        return adj_score

    def get_keywords(self):
        results = dbutil.get_seed_data()
        keywords = []
        for row in results:   
            keyws = row['keywords'].split(',')
            for kwyw in keyws:
                kw = kwyw.split()
                str_k = ''
                for k in kw:
                    str_k += lemmatizer.lemmatize(k) + ' '
                keywords.append(str_k.strip())
        keywords = sorted(set(keywords), key = lambda x: keywords.count(x), reverse=True)
        return keywords


