import pytextrank
import pandas as pd
import spacy 
from app.MySQLUtility import MySQLUtility
from app.PreProcessText import PreProcessText

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("textrank")
str_process = PreProcessText()
dbutil = MySQLUtility()    

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
                keyword.append(stringkeyword.lower().strip())
        res = sorted(set(keyword), key = lambda x: keyword.count(x), reverse=True)
        return res

    def extract_keyword_seed_data(self):            
        results = dbutil.get_seed_data()
        batch_update = []
        for row in results: 
            content = row['content'] 
            id = row['id']
            if content != None and len(content) > 1: 
                sentences = str_process.get_sentences(content)
                for stmt in sentences: 
                    stmt = str(stmt)
                    if len(stmt) > 0:   
                        keywords =  self.text_rank(stmt)
                        keywords = ", ".join(keywords)   
                        query_json = {"id": id, "keywords":keywords}  
                        batch_update.append(query_json)

        dbutil.update_seed_data_batch(batch_update)