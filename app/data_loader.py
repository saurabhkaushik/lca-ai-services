from app.MySQLUtility import MySQLUtility
from app.TextRank_Extractor import TextRank_Extractor
import json 
import csv
import os 
from app.PreProcessText import PreProcessText

processTxt = PreProcessText()
dbutil = MySQLUtility()
cuda_data_file = './cuad-data/CUAD/CUADv1.json'
reports_folder = './cuad-data/reports/'
seed_data_file = './cuad-data/seed_data.csv'

class Data_Loader: 
    def __init__(self) -> None:
        pass

    def import_cuad_contract_data(self):
        with open(cuda_data_file) as json_file:
            data = json.load(json_file)
        for data_row in data['data']:
            contract = data_row['paragraphs'][0]['context']
            title = data_row['title']
            dbutil.save_contracts(title.rstrip(), contract.rstrip())
        return None

    def import_reports_contract_data(self):    
        filelist = os.listdir(reports_folder)   
        batch_insert = []    

        for file_name in filelist:  
            if file_name.endswith(".txt"):
                print("Working with ", file_name)
                with open(reports_folder + file_name, encoding= "ISO-8859-1") as report_file:
                    filestr = report_file.read()
                    insert_json =  {"title" : file_name, "content" : filestr,  "type" : "curated", "response" : "", "domain" : "liability", "userid" : "admin"}               
                    batch_insert.append(insert_json)
                report_file.close()
        dbutil.save_contracts_batch(batch_insert)
        return None

    def import_seed_data(self):  
        text_rank = TextRank_Extractor()      
        with open(seed_data_file, newline='', encoding='utf-8') as csvfile:
            seedreader = csv.reader(csvfile)
            line_count = 0
            for row in seedreader:
                if line_count > 0:
                    keywords =  text_rank.text_rank(row[0].rstrip()) 
                    keywords = ", ".join(keywords)  
                    dbutil.save_seed_data(keywords.rstrip().lower().strip(), row[0].rstrip(), row[1].rstrip().lower().strip())
                line_count += 1
        csvfile.close()

    def import_seed_data_batch(self):  
        text_rank = TextRank_Extractor()  
        batch_insert = []    
        with open(seed_data_file, newline='', encoding='utf-8') as csvfile:
            seedreader = csv.reader(csvfile)
            line_count = 0
            for row in seedreader:
                if line_count > 0:
                    keywords =  text_rank.text_rank(row[0].rstrip()) 
                    keywords = ", ".join(keywords).rstrip().lower().strip()  
                    label = row[1].rstrip().lower().strip()
                    content = row[0].rstrip()
                    insert_json = {"keywords" : keywords, "content" : content, "label" : label, "type" : 'curated', "domain" : 'liability', "userid" : 'admin'}
                    batch_insert.append(insert_json)

                line_count += 1
        dbutil.save_seed_data_batch(batch_insert)
        csvfile.close()
        
    def load_seed_to_training_data(self):        
        results = dbutil.get_seed_data()
        for row in results: 
            content = row['content']   
            label = row['label']            
            if content != None and len(content) > 0: 
                sentences = processTxt.get_sentences(content)
                #sentences = re.split(r' *[\.\?!][\'"\)\]]* *', content) 
                for sentence in sentences: 
                    sentence = str(sentence)
                    if len(sentence) > 4:   
                        print (">> Inseted Statements : ", sentence, " Label: ", label)
                        dbutil.save_training_data(sentence, "seed", label=label.lower().strip(), score=100)
        return
    
    def load_seed_to_training_data_batch(self):
        batch_insert = []    

        results = dbutil.get_seed_data()
        for row in results: 
            content = row['content']   
            label = row['label']            
            if content != None and len(content) > 0: 
                sentences = processTxt.get_sentences(content)
                #sentences = re.split(r' *[\.\?!][\'"\)\]]* *', content) 
                for sentence in sentences: 
                    sentence = str(sentence)
                    if len(sentence) > 4:   
                        #print (">> Statements : ", sentence, " Label: ", label)
                        insert_json = {"content" : sentence, "type" : "seed", "label" : label, "eval_label" : '', "score" : 0, "eval_score" : 0, "domain" : "liability", "userid" : "admin"}
                        batch_insert.append(insert_json)
        dbutil.save_training_data_batch(batch_insert)
        return

    '''
    def prep_keywords_training_data(self):
        with open(self.keywords_data_file) as data_file:
            for line in data_file:
                if len(line.rstrip()) > 0:
                    print(line.rstrip())
                    self.dbutil.save_learndb(line.rstrip(), "")


    def prep_statement_training_data(self):
        with open(self.statements_data_file) as data_file:
            for line in data_file:
                if len(line.rstrip()) > 0:
                    print(line.rstrip())
                    self.dbutil.save_learndb("", line.rstrip())
    '''


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
