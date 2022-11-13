from app.BQUtility import BQUtility
import spacy 
from nltk.stem import WordNetLemmatizer
  
lemmatizer = WordNetLemmatizer()
nlp = spacy.load('en_core_web_sm')
dbutil = BQUtility()

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
    
    def adjust_score(self, count, total, score):
        adj_score = score + (((count * 100) / total) * score)
        return adj_score

    def calculate_score(self, sentence, score, keywords):
        neg_score = 0
        doc = nlp(str(sentence))
        for e in doc.ents:
            print(e.text, e._.negex)
            etxt =  lemmatizer.lemmatize(e.text)
            if etxt in keywords:
                neg_score = (neg_score - 1) if e._.negex == True else (neg_score + 1)
        adj_score = self.adjust_score(neg_score, len(sentence), score)
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


