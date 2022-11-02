import json
import string
import spacy
import re
from gensim.models import Word2Vec
import spacy

nlp = spacy.load("en_core_web_sm")
stopwords = nlp.Defaults.stop_words

#seed_data_file = "./cuad-data/seed_contract_data.json"
#domain_terms_file = "./cuad-data/domain_terms.json"
training_data_file = "./cuad-data/key_train_data.json"

'''
def load_data():
    with open(seed_data_file) as json_file:
        data = json.load(json_file)
    dataset = data["contract"]
    return dataset

def load_terms():
    with open(domain_terms_file) as json_file:
        data = json.load(json_file)
    terms = data['terms']
    return terms

def save_terms(terms_set):
    terms = load_terms()
    for term in terms_set: 
        terms.append(term.strip().lower())
    new_term = [*set(terms)]
            
    new_terms = {"terms" : new_term}
    with open(domain_terms_file, 'w') as fp:
        json.dump(new_terms, fp)
    return new_terms
'''

def extract_verbs(sentences):
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
def highlight_sentences(contract):
    helper = PreProcessText()
    #article_text = helper.prep_data() 
    article_text = contract
    words = helper.token_words(text=article_text)
    model = Word2Vec([words], min_count=1)
    catchwords = load_terms() 
    
    catch_stmt = {}
    return_value = {}
    sim_words =[]

    print("Contract: \n\"", article_text, "\" \n")
    print("Catch Words: ", catchwords, "\n")
    for c_word in catchwords: 
        print(">>>> Searching Word: \"", c_word, "\"" )
        try : 
            sim_words = model.wv.most_similar(c_word)
            print (">>>>  Similar Words 1: \"", sim_words)
        except KeyError: # TODO: Why this is thrown ?? 
            print (">>>> Words Similar to \"" + c_word + "\" not found.")
        print (">>>>  Similar Words 2: \"", sim_words)
        for s_word in sim_words:
            print (">>>>>>>> Similar word \"" , s_word[0] , "\" of \"", c_word, "\" Searching ...")
            catch_stmt[s_word[0]] = [sentence + '.' for sentence in article_text.split('.') if s_word[0] in sentence]
            try: 
                print (">>>>>>>>  Found Sentence : ", catch_stmt[s_word[0]][0])
                res = re.search(catch_stmt[s_word[0]][0], article_text)
                if res:
                    print(">>>>>>>> Index : ", res.start(), res.end())
                    print(">>>>>>>>  Output String : ", article_text[res.start() : res.end()])   
                    stmt_index = str(res.start()) + "-" + str(res.end())
                    if stmt_index in return_value.keys():                           
                        relevence = return_value[stmt_index]["relevence"] + 10
                    else:    
                        relevence = 10
                    return_value[stmt_index] = {"start_index" : res.start(), "end_index" : res.end(), "relevence" : relevence}
            except IndexError:
                print (">>>>>>>> Word Not Found")
    print ("return_value : \n", return_value)

    return return_value
'''

def highlight_ranking(return_value):
    high_score = 0 
    for r_key in return_value:
        if high_score < return_value[r_key]['relevence']:
            high_score = return_value[r_key]['relevence']
    #print ("Highest Score:", high_score)
    for r_key in return_value:
        score = 100 * return_value[r_key]['relevence'] / high_score 
        #print(return_value[r_key]['relevence'] , " >> " , score)
        if score > 67: 
            return_value[r_key]["relevence_degree"] = "HIGH"
        else: 
            if score > 34: 
                return_value[r_key]["relevence_degree"] = "MEDIUM"
            else:
                if score > 0: 
                    return_value[r_key]["relevence_degree"] = "LOW"

    print ("return_value : \n", return_value)
    return return_value

def generate_training_corpus(keywords, statements):
    helper = PreProcessText()
    #article_text = helper.prep_data() 
    article_text = statements
    words = helper.token_words(text=article_text)
    model = Word2Vec([words], min_count=1)
    #catchwords = keywords
    json_struct = {"train" : []}
    sim_words =[]

    print("Contract: \n\"", article_text, "\" \n")
    print("Catch Words: ", keywords, "\n")
    
    for set_keywords in keywords:
        catchwords = set_keywords.strip().split(',')
        for c_word in catchwords: 
            print(">>>> Searching Word: \"", c_word, "\"" )
            try : 
                sim_words = model.wv.most_similar(c_word)
                print (">>>>  Similar Words 1: \"", sim_words)
            except KeyError: # TODO: Why this is thrown ?? 
                print (">>>> Words Similar to \"" + c_word + "\" not found.")
            print (">>>>  Similar Words 2: \"", sim_words)
            catch_stmt = {}
            for stmts in article_text:
                for s_word in sim_words:
                    #print (">>>>>>>> Similar word \"" , s_word[0] , "\" of \"", c_word, "\" Searching ...")
                    t_sentence = [sentence + '.' for sentence in stmts.split('.') if s_word[0] in sentence]
                    #print(s_word[0])
                    if len(t_sentence) > 0:
                        t_label = s_word[0].lower().strip()
                        catch_stmt = {"sentence" : t_sentence[0], "label" : t_label}
                        #print (json_struct)
                        json_struct["train"].append(catch_stmt)

    with open(training_data_file, 'w') as fp:
        json.dump(json_struct, fp)
