import pandas as pd
from app.PreProcessText import PreProcessText

pre_process = PreProcessText()
min_sentence_len = 10

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
            if content != None and len(content) > min_sentence_len:
                sentences = pre_process.get_sentences(content)
                for stmt in sentences:
                    stmt = str(stmt['sentance'])
                    if len(stmt) > min_sentence_len:
                        keywords = self.text_rank(stmt)
                        keywords = ", ".join(keywords)
                        if len(keywords) > int(min_sentence_len / 2):
                            query_json = {"id": id, "keywords": keywords}
                            batch_update.append(query_json)
        self.dbutil.update_seed_data_batch(batch_update)
