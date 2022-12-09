from transformers import pipeline
from app.PreProcessText import PreProcessText
import json 
preprocess = PreProcessText()
import re
from os.path import exists
import logging

sentiment_model = "distilbert-base-uncased-finetuned-sst-2-english"
polarity_folder = './data/' 
file_name = '_key_polarity.json'
polarity_accuracy = 'high' # 'high'/'low'
min_sentence_len = 10

class Risk_Score_Service(object):
    sentiment_pipeline = pipeline(
        "sentiment-analysis", model=sentiment_model)
    domain_key_polarity = {}
    dbutil = None 
    domains = None

    def __init__(self, dbutil, domains):
        self.dbutil = dbutil  
        self.domains = domains      
        pass

    def load_polarity_data(self):
        for domain in self.domains:
            if not domain in self.domain_key_polarity.keys():
                if exists(polarity_folder + domain + file_name ):
                    with open(polarity_folder + domain + file_name) as json_file:
                        self.domain_key_polarity[domain] = json.load(json_file)
                else: 
                    logging.error('Polarity File is Missing.' + ' : ' + domain)
        return 

    def get_sentiment_score(self, sentence):
        data = [sentence]
        sent_result = self.sentiment_pipeline(data)
        #print (sent_result)
        sent_score = (
            sent_result[0]['score']) if sent_result[0]['label'] == 'POSITIVE' else -(sent_result[0]['score'])
        sent_score = int (sent_score * 100)
        return sent_score
    
    def get_context_score(self, text, domain): 
        context_score = 0
        count = 0
        sem_score = self.get_sentiment_score(text)
        text_lem = preprocess.get_lemmantizer(text)     
        key_polarity = self.domain_key_polarity[domain]['keywords']   
        for key_dic in key_polarity:            
            if key_dic['name'] in text_lem:  
                #print('Polarity Word Found : \'' + key_dic['name'] + '\'')
                pol_score = key_dic['polarity']
                if sem_score >= 0:
                    context_score += pol_score
                else:
                    context_score += -pol_score
                count += 1
                if polarity_accuracy == 'low':
                    break # TODO: Ideally take average of all keyword's polarity 
        if not count == 0:
            context_score = int (context_score / count)

        if context_score == 0: 
            context_score = self.get_sentiment_score(text)
        
        context_score = int (50 + (context_score / 2))
        #print ('Test 3')
        return context_score

    def process_keyword_polarity(self, domain):         
        self.domain_key_polarity[domain] = {}
        key_polarity = []
        keywords = self.get_keywords(domain)     
        for kwrd in keywords: 
            key_scr = {}
            key_scr['name'] = str(kwrd)
            key_scr['score'] = 0
            key_scr['count'] = 0
            key_scr['polarity'] = 0
            key_polarity.append(key_scr)

        results = self.dbutil.get_training_data(domain)
        for row in results:
            text = row["content"]
            text_lem = preprocess.get_lemmantizer(text)
            for key_dic in key_polarity:
                if key_dic['name'] in text_lem:
                        key_dic['score'] += int(self.get_sentiment_score(text))
                        key_dic['count'] += 1

        for key_dic in key_polarity:
            if key_dic['count'] == 0:
                key_polarity.remove(key_dic)
            else:
                key_dic['polarity'] = int((key_dic['score']) / key_dic['count'])
        
        self.domain_key_polarity[domain]['keywords'] = key_polarity
            
        with open(polarity_folder + domain + file_name, "w") as outfile:
            json.dump(self.domain_key_polarity[domain], outfile)

        print ('Polarity : \n', self.domain_key_polarity)
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
                str_k = str_k.strip()
                if len (str_k) > int(min_sentence_len / 2):
                    keywords.append(str_k)
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