import json
import string
import spacy
from gensim.models import Word2Vec
import spacy

from app.BQUtility import BQUtility

'''
from sentence_transformers import SentenceTransformer, util
nlp = spacy.load("en_core_web_sm")
stopwords = nlp.Defaults.stop_words
sim_model = SentenceTransformer('all-MiniLM-L6-v2')
'''

training_data_file = "./cuad-data/lca_train_data.json"

class highlight_service:

    def __init__(self) -> None:
        pass

    ''' 
    def load_train_data(self):
        with open(training_data_file) as json_file:
            data = json.load(json_file)
        dataset = data['train']
        return dataset    

    def extract_keywords(self, sentences):
        verbs_list = set()
        for stmts in sentences:
            t_sentence = [sentence + '.' for sentence in stmts.split('.')]
            for stmt in t_sentence:
                doc = nlp(stmt)    
                verbs = [token.text.strip().lower() for token in doc if (token.pos_ == "VERB" and not token.text.strip().lower() in stopwords)]  
                if len(verbs) > 0:
                    verbs = set(verbs)
                    verbs_list.update(verbs)  
        print("Collected Verbs : ", verbs_list)
        return verbs_list


    def seed_training_corpus(self):
        dbutil = BQUtility()    
        keywords = []

        results = dbutil.get_learndb()
        for row in results: 
            keyword = row['keywords']
            if len(keyword) > 0:
                keywords.append(keyword.lower().strip())
        
        results = dbutil.get_learndb()
        for row in results: 
            statement = row['statements']               
            if len(statement) > 0: 
                for k_word in keywords:
                    t_sentence = [sentence + '.' for sentence in statement.split('.') if k_word in sentence]
                    for stmt in t_sentence: 
                        if len(stmt) > 0:                    
                            catch_stmt = {"sentence" : stmt, "label" : k_word}
                            print (">>>>>>> Catch Stmt: ", catch_stmt)
                            dbutil.save_training_data(catch_stmt["sentence"], catch_stmt["label"], "seed", "")
        return
    '''
    
    def seed_training_load(self):
        dbutil = BQUtility()    
        
        results = dbutil.get_learndb()
        for row in results: 
            statement = row['statements']   
            label = row['label']            
            if len(statement) > 0: 
                t_sentence = [sentence + '.' for sentence in statement.split('.')]
                for stmt in t_sentence: 
                    if len(stmt) > 2:   
                        #print ("Length of Stmt: ", len(stmt))                 
                        catch_stmt = {"sentence" : stmt, "label" : label}
                        print (">>>>>>> Catch Stmt: ", catch_stmt)
                        dbutil.save_training_data(catch_stmt["sentence"], catch_stmt["label"], "seed", "")
        return

    ''' 
    def seed_training_corpus_similarity(self):
        dbutil = BQUtility()    
        keywords = []

        results = dbutil.get_learndb()
        for row in results: 
            keyword = row['keywords']
            if len(keyword) > 0:
                keywords.append(keyword.lower().strip())
        
        results = dbutil.get_learndb()
        for row in results: 
            statement = row['statements']               
            if len(statement) > 0: 
                for k_word in keywords:    
                    t_sentence = [sentence + '.' for sentence in statement.split('.')]
                    for stmt in t_sentence: 
                        #en_1 = sim_model.encode(k_word)
                        #en_2 = sim_model.encode(stmt)
                        result = util.cos_sim(en_1, en_2)
                        print(result.item())
                        if len(stmt) > 0:                    
                            catch_stmt = {"sentence" : stmt, "label" : k_word}
                            print (">>>>>>> Catch Stmt: ", catch_stmt)
                            dbutil.save_training_data(catch_stmt["sentence"], catch_stmt["label"], "seed", "")
        return
    '''

    def highlight_ranking(self, return_value):
        for r_key in return_value:
            score = return_value[r_key]['relevence'] 
            if score > 67: 
                return_value[r_key]["relevence_degree"] = "HIGH"
            else: 
                if score > 34: 
                    return_value[r_key]["relevence_degree"] = "MEDIUM"
                else:
                    if score > 0: 
                        return_value[r_key]["relevence_degree"] = "LOW"
        return return_value

''' 
# Text Processing Class 
class PreProcessText(object):
    def __init__(self):
        pass

    def __remove_punctuation(self, text):
        """
        Takes a String
        return : Return a String
        """
        message = []
        for x in text:
            if x in string.punctuation:
                pass
            else:
                message.append(x)
        message = ''.join(message)

        return message

    def __remove_stopwords(self, text):
        """
        Takes a String
        return List
        """
        words= []
        for x in text.split():

            if x.lower() in stopwords:
                pass
            else:
                words.append(x)
        return words

    def token_words(self,text=''):
        message = self.__remove_punctuation(text)
        words = self.__remove_stopwords(message)
        return words

'''