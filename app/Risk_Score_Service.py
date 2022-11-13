from app.BQUtility import BQUtility
import spacy 
from nltk.stem import WordNetLemmatizer
  
lemmatizer = WordNetLemmatizer()
nlp = spacy.load('en_core_web_sm')
dbutil = BQUtility()
from transformers import pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

class Risk_Score_Service:

    def __init__(self) -> None:
        pass

    def highlight_ranking(self, return_value):
        for r_key in return_value:
            score = return_value[r_key]['relevence'] 
            if score > 67: 
                return_value[r_key]["relevence_degree"] = "HIGH"
            else: 
                if score > 34: 
                    return_value[r_key]["relevence_degree"] = "MEDIUM"
                else:
                    if score > 0: 
                        return_value[r_key]["relevence_degree"] = "LOW"
        return return_value
    
    def adjust_score(self, sent_score, score):
        print (sent_score, score)
        adj_score = score + ((sent_score * score) / 200)
        return adj_score

    def calculate_score(self, sentence, score):
        neg_score = 0
        doc = nlp(str(sentence))
        data = [sentence] 
        sentr = sentiment_pipeline(data)
        #print(sentr)
        sent_score = (sentr[0]['score']) if sentr[0]['label'] == 'POSITIVE' else -(sentr[0]['score'])
        sent_score = sent_score * 100.00
        adj_score = self.adjust_score(sent_score, score)
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


