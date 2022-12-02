from transformers import pipeline
from app.PreProcessText import PreProcessText
import json 
preprocess = PreProcessText()

sentiment_model = "distilbert-base-uncased-finetuned-sst-2-english"
polarity_file = './data/key_polarity.json'

class Risk_Score_Service:
    sentiment_pipeline = pipeline(
        "sentiment-analysis", model=sentiment_model)
    domain_key_polarity = None
    dbutil = None 

    def __init__(self, dbutil):
        self.dbutil = dbutil        
        pass

    def load_polarity_data(self):
        if self.domain_key_polarity == None:
            with open(polarity_file) as json_file:
                self.domain_key_polarity = json.load(json_file)
        return 

    def get_sentiment_score(self, sentence):
        data = [sentence]
        sent_result = self.sentiment_pipeline(data)
        #print (sent_result)
        sent_score = (
            sent_result[0]['score']) if sent_result[0]['label'] == 'POSITIVE' else -(sent_result[0]['score'])
        sent_score = sent_score * 100
        return sent_score
    
    def get_context_score(self, text, domain): 
        context_score = 0
        sem_score = self.get_sentiment_score(text)
        text_lem = preprocess.get_lemmantizer(text)     
        key_polarity = self.domain_key_polarity[domain]   

        for key_dic in key_polarity:
            if key_dic['name'] in text_lem:            
                pol_score = key_dic['polarity']
                if pol_score >=0 and sem_score >= 0:
                    context_score = pol_score
                elif pol_score >=0 and sem_score < 0:
                    context_score = -pol_score
                elif pol_score < 0 and sem_score >= 0:
                    context_score = pol_score
                elif pol_score < 0 and sem_score < 0:
                    context_score = -pol_score
            else: 
                context_score = self.get_sentiment_score(text)

        print ('get_context_score : ', text, context_score)
        return context_score

    def process_keyword_polarity(self, domains):         
        self.domain_key_polarity = {}
        for domain in domains:
            key_polarity = []
            keywords = self.get_keywords(domain)     
            for kwrd in keywords: 
                key_scr = {}
                key_scr['name'] = str(kwrd)
                key_scr['score'] = 0
                key_scr['count'] = 0
                key_scr['polarity'] = 0
                key_polarity.append(key_scr)

            results = self.dbutil.get_training_data(domain, type="seed")
            for row in results:
                text = row["content"]
                text_lem = preprocess.get_lemmantizer(text)
                for key_dic in key_polarity:
                    if key_dic['name'] in text_lem:
                            key_dic['score'] += int(self.get_sentiment_score(text))
                            key_dic['count'] += 1

            for key_dic in key_polarity:
                if not key_dic['count'] == 0:
                    key_dic['polarity'] = int((key_dic['score']) / key_dic['count'])
            
            self.domain_key_polarity[domain] = key_polarity
            
        with open(polarity_file, "w") as outfile:
            json.dump(self.domain_key_polarity, outfile)

        #print (self.domain_key_polarity)
        return

    def get_keywords(self, domain):
        results = self.dbutil.get_seed_data(domain)
        keywords = []
        for row in results:
            keyws = row['keywords'].split(',')
            for kwyw in keyws:
                kw = kwyw.split()
                str_k = ''
                for k in kw:
                    str_k += preprocess.get_lemmantizer(k) + ' '
                keywords.append(str_k.strip())
        keywords = sorted(
            set(keywords), key=lambda x: keywords.count(x), reverse=True)
        return keywords

''' 
    def get_semantic_score(self, sentence):
        score = 0        
        nlp = preprocess.get_nlp()
        
        doc = nlp(sentence)
        for token in doc:
            if (token.pos_ == "ADJ" or token.pos_ == "VERB") and (not token.is_stop):
                doc1 = nlp(token.text)
                doc2 = nlp("increase")
                doc3 = nlp("decrease")
                d_positive = doc1.similarity(doc2)
                d_negative = doc1.similarity(doc3)

                diff_d = abs(d_positive - d_negative)
                if diff_d > 0.01:
                    score += 1
                else:
                    score -= 1
        if score >= 0:
            s_score = 100.0
        else:
            s_score = -100.0
        return s_score
'''