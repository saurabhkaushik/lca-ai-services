import pytextrank
import pandas as pd
import spacy 
from app.BQUtility import BQUtility
from app.PreProcessText import PreProcessText

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("textrank")

str_process = PreProcessText()

class TextRank_Extractor: 
    def __init__(self) -> None:
        pass 

    def text_rank(self, text):
        doc = nlp(text)
        keyword = []
        for phrase in doc._.phrases:
            str_key = str_process.token_words(text=phrase.text)
            stringkeyword = " ".join(str_key)
            if len(stringkeyword) > 0:
                keyword.append(stringkeyword.lower())
        res = sorted(set(keyword), key = lambda x: keyword.count(x), reverse=True)
        return res

    def extract_keyword_seed_data(self):
        dbutil = BQUtility()    
            
        results = dbutil.get_seed_data()
        for row in results: 
            content = row['content'] 
            id = row['id']
            label = row['label']
            if len(content) > 0: 
                t_sentence = [sentence + '.' for sentence in content.split('.')]
                for stmt in t_sentence: 
                    if len(stmt) > 0:   
                        keywords =  self.text_rank(stmt) 
                        keywords = ", ".join(keywords)                 
                        dbutil.update_seed_data_id(id, keywords, content, label)