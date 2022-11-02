import json
import string
import spacy
from gensim.models import Word2Vec
import spacy

from app.BQUtility import BQUtility

nlp = spacy.load("en_core_web_sm")
training_data_file = "./cuad-data/lca_train_data.json"
stopwords = nlp.Defaults.stop_words

class highlight_service:

    def __init__(self) -> None:
        pass

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

    def generate_training_corpus(self, keywords, statements):
        helper = PreProcessText()
        article_text = statements
        words = helper.token_words(text=article_text)
        model = Word2Vec([words], min_count=1)
        json_struct = {"train" : []}
        sim_words =[]
        dbutil = BQUtility()

        for set_keywords in keywords:
            catchwords = set_keywords.strip().split(',')
            for c_word in catchwords: 
                try : 
                    sim_words = model.wv.most_similar(c_word)
                except KeyError: # TODO: Why this is thrown ?? 
                    print (">>>> Words Similar to \"" + c_word + "\" not found.")
                catch_stmt = {}
                for stmts in article_text:
                    for s_word in sim_words:
                        t_sentence = [sentence + '.' for sentence in stmts.split('.') if s_word[0] in sentence]
                        if len(t_sentence) > 0:
                            t_label = s_word[0].lower().strip()
                            catch_stmt = {"sentence" : t_sentence[0], "label" : t_label}
                            json_struct["train"].append(catch_stmt)
                            #print ("catch_stmt :", catch_stmt)
                            dbutil.save_training_data(catch_stmt["sentence"], catch_stmt["label"])

        with open(training_data_file, 'w') as fp:
            json.dump(json_struct, fp)
    
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