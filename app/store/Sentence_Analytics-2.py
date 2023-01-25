import spacy
from app.PreProcessText import PreProcessText
from app.Transformer_Service import Transformer_Service
from datetime import datetime
import parsedatetime as pdt
from word2number import w2n
import re

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
        money_list = []
        date_list = []
        for ent in doc.ents:
            print(ent.text, ent.start_char, ent.end_char, ent.label_)
            # Extract the Money 
            if ent.label_ == 'MONEY':
                money = 0
                money_num = 0
                money_str = ent.text

                # Extract from '$1.456 billion' to 145600000000 
                m_str_list = money_str.split()
                for m_word in m_str_list:
                    m_word = m_word.replace(',', '')
                    temp = re.findall(r'-?\d+\.?\d*', m_word)
                    res = list(map(float, temp))
                    print(res)
                    if (len(res) > 0):
                        money_num += res[0]

                try:
                    money = w2n.word_to_num(money_str)
                except Exception as e:
                    print(e)
                print('Money w2n:', money)
                if money_num != 0 and money_num != money:
                    money = money_num * money

                money_list.append({'c_money': money, 'o_money': ent.text})
                print(ent.text + '>>' + str(money))

            # Extract Dates
            if ent.label_ == 'DATE':
                date_time_obj = cal.parseDT(ent.text, now)[0]
                date_list.append(
                    {'c_date': str(date_time_obj), 'o_date': ent.text})
                print(ent.text + '>>' + str(date_time_obj))

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
            data_dict['polarity'] = -1 if risk_resp >= 60 else 1
            response_list.append(data_dict)

        return response_list

    def process_request(self, contract, domain):
        contract = self.preprocess.get_sentences_spacy(contract)
        response_obj = []
        for sent in contract:
            sent = str(sent)
            data_list = self.analyze(sent, domain)
            for data_dict in data_list:
                response_obj.append(data_dict)

        # print ('Sentence Analysis: ', response_obj)
        return response_obj
