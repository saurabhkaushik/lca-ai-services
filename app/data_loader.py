from app.BQUtility import BQUtility
from app.TextRank_Extractor import TextRank_Extractor
import json 
import csv
import os 
from app.PreProcessText import PreProcessText
processTxt = PreProcessText()
dbutil = BQUtility()
cuda_data_file = './cuad-data/CUADv1.json'
keywords_data_file = './cuad-data/keywords.txt'
statements_data_file = './cuad-data/statements.txt'
seed_data_file = './cuad-data/seed_data.csv'
reports_folder = './cuad-data/reports/'

class Data_Loader: 
    def __init__(self) -> None:
        pass

    def import_contract_data(self):
        with open(self.cuda_data_file) as json_file:
            data = json.load(json_file)
        for data_row in data['data']:
            contract = data_row['paragraphs'][0]['context']
            title = data_row['title']
            self.dbutil.save_contracts(title, contract, "")
        return 

    def import_reports_data(self):    
        filelist = os.listdir(self.reports_folder)   
        for file_name in filelist:  
            if file_name.endswith(".txt"):
                print("Working with ", file_name)
                with open(self.reports_folder + file_name, encoding= "ISO-8859-1") as report_file:
                    filestr = report_file.read()
                    self.dbutil.save_contracts(file_name, filestr, "")
                report_file.close()

    def import_seed_data(self):  
        text_rank = TextRank_Extractor()      
        with open(self.seed_data_file, newline='', encoding='utf-8') as csvfile:
            seedreader = csv.reader(csvfile)
            line_count = 0
            for row in seedreader:
                if line_count > 0:
                    keywords =  text_rank.text_rank(row[0].rstrip()) 
                    keywords = ", ".join(keywords)  
                    self.dbutil.save_seed_data(keywords, row[0].rstrip(), row[1].rstrip())
                line_count += 1
        csvfile.close()
        
    def load_seed_to_training_data(self):
        dbutil = BQUtility()    
        
        results = dbutil.get_seed_data()
        for row in results: 
            content = row['content']   
            label = row['label']            
            if len(content) > 0: 
                sentences = processTxt.get_sentences(content)
                #sentences = re.split(r' *[\.\?!][\'"\)\]]* *', content) 
                for sentence in sentences: 
                    sentence = str(sentence)
                    if len(sentence) > 4:   
                        print (">> Inseted Statements : ", sentence, " Label: ", label)
                        dbutil.save_training_data(sentence, label.lower().strip(), "seed", "")
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
