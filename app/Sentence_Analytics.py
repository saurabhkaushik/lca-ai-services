import spacy
from app.PreProcessText import PreProcessText
from app.Transformer_Service import Transformer_Service
from datetime import datetime
import parsedatetime as pdt 
#import datefinder
from word2number import w2n

nlp = spacy.load("en_core_web_md")
cal = pdt.Calendar()
now = datetime.now()

class Sentence_Analytics(object):
    preprocess = PreProcessText()
    trans_service = None
    risk_service = None

    def __init__(self, trans_service, risk_service):
        self.trans_service = trans_service
        self.risk_service = risk_service
        pass

    def analyze(self, text, domain):
        doc = nlp(text)
        data_dict = {}
        data_dict['text'] = text
        for ent in doc.ents:        
            #print(ent.text, ent.start_char, ent.end_char, ent.label_)
            if ent.label_ == 'MONEY':
                money = w2n.word_to_num(ent.text)
                data_dict['c_money'] = str(money)
                data_dict['o_money'] = ent.text
                print (ent.text + '>>' + str(money))
            if ent.label_ == 'DATE':    
                date_time_obj = cal.parseDT(ent.text, now)[0]   
                data_dict['c_date'] = str(date_time_obj)
                data_dict['o_date'] = ent.text 
                #print (ent.text + '>>' + str(date_time_obj))
                ''' 
                matches = datefinder.find_dates(ent.text)                
                print (ent.text + '>>' + str(date_time_obj))
                for match in matches:
                    print ('Match : ' + ent.text + '>>' + str(match))
                '''

        for token in doc:
            if (token.pos_ == "VERB"): # and (not token.is_stop):
                data_dict['verb'] = token.text
        
        trans_resp = self.trans_service.process_text(text, domain)
        if trans_resp:
            data_dict['label'] = trans_resp['label']
            data_dict['p_score'] = trans_resp['score']
        else:
            data_dict['label'] = ''
            data_dict['p_score'] = 0

        risk_resp = self.risk_service.get_sentiment_score(text)
        data_dict['polarity'] = 1 if risk_resp > 0 else -1

        return data_dict

    def process_request(self, contract, domain):
        contract = self.preprocess.get_sentences_regex(contract)
        response_obj = []
        for sent in contract: 
            sent = str(sent)
            data_dict = self.analyze(sent, domain)
            response_obj.append(data_dict)

        #print ('Sentence Analysis: ', response_obj)
        return response_obj
