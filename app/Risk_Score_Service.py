from transformers import pipeline
from app.PreProcessText import PreProcessText

preprocess = PreProcessText()

sentiment_model = "distilbert-base-uncased-finetuned-sst-2-english"

class Risk_Score_Service:
    sentiment_pipeline = pipeline(
        "sentiment-analysis", model=sentiment_model)

    dbutil = None 
    def __init__(self, dbutil):
        self.dbutil = dbutil
        pass

    def get_sentiment_score(self, sentence):
        data = [sentence]
        sent_result = self.sentiment_pipeline(data)
        #print (sent_result)
        sent_score = (
            sent_result[0]['score']) if sent_result[0]['label'] == 'POSITIVE' else -(sent_result[0]['score'])
        sent_score = sent_score * 100
        return sent_score

    def get_semantic_score(self, sentence):
        score = 0        
        nlp = preprocess.get_nlp()
        
        doc = nlp(sentence)
        for token in doc:
            if (token.pos_ == "ADJ" or token.pos_ == "VERB") and (not token.is_stop):
                doc1 = nlp(token.text)
                doc2 = nlp("positive")
                doc3 = nlp("negative")
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
