import pandas as pd
from app.PreProcessText import PreProcessText

pre_process = PreProcessText()


class TextRank_Extractor:
    dbutil = None 
    def __init__(self, dbutil):
        self.dbutil = dbutil
        pass

    def text_rank(self, text):
        nlp = pre_process.get_nlp()
        doc = nlp(text)
        keyword = []
        for phrase in doc._.phrases:
            str_key = pre_process.token_words(text=phrase.text)
            stringkeyword = " ".join(str_key)
            if len(stringkeyword) > 0:
                stringkeyword = pre_process.preprocess_text(stringkeyword)
                keyword.append(stringkeyword.lower().strip())
        res = sorted(
            set(keyword), key=lambda x: keyword.count(x), reverse=True)
        return res

    def extract_keyword_seed_data(self, domain):
        results = self.dbutil.get_seed_data(domain)
        batch_update = []
        for row in results:
            content = row['content']
            id = row['id']
            if content != None and len(content) > 1:
                sentences = pre_process.get_sentences(content)
                for stmt in sentences:
                    stmt = str(stmt['sentance'])
                    if len(stmt) > 0:
                        keywords = self.text_rank(stmt)
                        keywords = ", ".join(keywords)
                        if len(keywords) > 3:
                            query_json = {"id": id, "keywords": keywords}
                            batch_update.append(query_json)
        self.dbutil.update_seed_data_batch(batch_update)

    def get_keywords(self, domain):
        results = self.dbutil.get_seed_data(domain)
        keywords = []
        for row in results:
            keyws = row['keywords'].split(',')
            for kwyw in keyws:
                kw = kwyw.split()
                str_k = ''
                for k in kw:
                    str_k += pre_process.get_lemmantizer(k) + ' '
                keywords.append(str_k.strip())
        keywords = sorted(
            set(keywords), key=lambda x: keywords.count(x), reverse=True)
        return keywords
