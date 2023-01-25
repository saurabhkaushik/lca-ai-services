import spacy
from app.PreProcessText import PreProcessText
from app.Transformer_Service import Transformer_Service
from datetime import datetime
import parsedatetime as pdt
import re

nlp = spacy.load("en_core_web_md")
cal = pdt.Calendar()
now = datetime.now()

import nltk
import ssl
import lexnlp.extract.en.money

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')

class Numerical_Analytics(object):
    preprocess = PreProcessText()
    trans_service = None
    risk_service = None

    def __init__(self, trans_service, risk_service):
        self.trans_service = trans_service
        self.risk_service = risk_service
        pass

    def analyze(self, text, domain, threshold):
        doc = nlp(text)
        money_list = []
        date_list = []
        for ent in doc.ents:
            #print('Input Text: ', ent.text, ent.start_char, ent.end_char, ent.label_)
            # Extract the Money 
            if ent.label_ == 'MONEY':
                money = 0
                money_num = 0
                money_wrd = 0
                money_str = ent.text
                money_str = money_str.replace(',', '')
                mon_list = list(lexnlp.extract.en.money.get_money(money_str))
                if (len(mon_list) > 0):
                    money_num += mon_list[0][0]
                #print('Money money_num:', money_num)

                money = money_num
                money_list.append({'c_money': money, 'o_money': ent.text})
                print('Money Coversion: ' + ent.text + ' >> ' + str(money))

            # Extract Dates
            if ent.label_ == 'DATE':
                date_time_obj = cal.parseDT(ent.text, now)[0]
                date_list.append(
                    {'c_date': str(date_time_obj), 'o_date': ent.text})
                print('Date Coversion: ' + ent.text + ' >> ' + str(date_time_obj))

        response_list = []

        for money_d in money_list:
            data_dict = {}
            data_dict['c_money'] = money_d['c_money']
            data_dict['o_money'] = money_d['o_money']
            data_dict['text'] = text

            if len(date_list) > 0:
                data_dict['c_date'] = date_list[0]['c_date']
                data_dict['o_date'] = date_list[0]['o_date']
            else:
                data_dict['c_date'] = ''
                data_dict['o_date'] = ''

            for token in doc:
                if (token.pos_ == "VERB"):
                    data_dict['verb'] = token.text

            trans_resp = self.trans_service.process_text(text, domain)
            if trans_resp:
                data_dict['label'] = trans_resp['label']
                data_dict['p_score'] = trans_resp['score']
            else:
                data_dict['label'] = ''
                data_dict['p_score'] = 0

            # risk_resp = self.risk_service.get_sentiment_score(text)
            # data_dict['polarity'] = 1 if risk_resp > 0 else -1
            risk_resp = self.risk_service.get_context_score(text, domain)
            data_dict['polarity'] = 1 if risk_resp >= 40 else -1
            if (data_dict['p_score'] > threshold):
                response_list.append(data_dict)

        return response_list

    def process_request(self, contract, domain, threshold):
        contract = self.preprocess.get_sentences_spacy(contract)
        response_obj = []
        for sent in contract:
            sent = str(sent)
            data_list = self.analyze(sent, domain, threshold)
            for data_dict in data_list:
                response_obj.append(data_dict)

        # print ('Sentence Analysis: ', response_obj)
        return response_obj
