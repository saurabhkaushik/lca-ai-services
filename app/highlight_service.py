from gensim.models import Word2Vec
from app.BQUtility import BQUtility

class highlight_service:

    def __init__(self) -> None:
        pass
    
    def seed_training_load(self):
        dbutil = BQUtility()    
        
        results = dbutil.get_seed_data()
        for row in results: 
            content = row['content']   
            label = row['label']            
            if len(content) > 0: 
                t_sentence = [sentence + '.' for sentence in content.split('.')]
                for stmt in t_sentence: 
                    if len(stmt) > 2:   
                        #print ("Length of Stmt: ", len(stmt))                 
                        catch_stmt = {"sentence" : stmt, "label" : label.lower().strip()}
                        print (">>>>>>> Catch Stmt: ", catch_stmt)
                        dbutil.save_training_data(catch_stmt["sentence"], catch_stmt["label"], "seed", "")
        return

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
            content = row['content']               
            if len(content) > 0: 
                for k_word in keywords:
                    t_sentence = [sentence + '.' for sentence in content.split('.') if k_word in sentence]
                    for stmt in t_sentence: 
                        if len(stmt) > 0:                    
                            catch_stmt = {"sentence" : stmt, "label" : k_word}
                            print (">>>>>>> Catch Stmt: ", catch_stmt)
                            dbutil.save_training_data(catch_stmt["sentence"], catch_stmt["label"], "seed", "")
        return
    '''


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
            content = row['content']               
            if len(content) > 0: 
                for k_word in keywords:    
                    t_sentence = [sentence + '.' for sentence in content.split('.')]
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
