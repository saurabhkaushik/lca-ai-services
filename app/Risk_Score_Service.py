from app.BQUtility import BQUtility
import spacy 

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
        '''
        #print ('Sentence: ', sentence)
        #print('POS:')
        for token in doc:
            print(token.text,  token.pos_) 
        print('Negation:')
        ''' 
        for e in doc.ents:
            #print(e.text, e._.negex)
            if e.text in keywords:
                neg_score = (neg_score - 1) if e._.negex == True else (neg_score + 1)
        adj_score = self.adjust_score(neg_score, len(sentence), score)
        return adj_score

    def get_keywords(self):
        results = dbutil.get_seed_data()
        keywords = []
        for row in results:   
            keyw = row['keywords'].split(',')
            for k in keyw:
                keywords.append(k.strip())
        keywords = sorted(set(keywords), key = lambda x: keywords.count(x), reverse=True)
        print ('Keywords: ', keywords)
        return keywords


