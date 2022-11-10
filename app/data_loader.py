from app.BQUtility import BQUtility
from app.TextRank_Extractor import TextRank_Extractor
import json 
import csv
import os 
import re

class Data_Loader: 
    def __init__(self) -> None:
        pass

    dbutil = BQUtility()
    cuda_data_file = './cuad-data/CUADv1.json'
    keywords_data_file = './cuad-data/keywords.txt'
    statements_data_file = './cuad-data/statements.txt'
    seed_data_file = './cuad-data/seed_data.csv'
    reports_folder = './cuad-data/reports/'

    def prep_contract_data(self):
        with open(self.cuda_data_file) as json_file:
            data = json.load(json_file)
        for data_row in data['data']:
            contract = data_row['paragraphs'][0]['context']
            title = data_row['title']
            self.dbutil.save_contracts(title, contract, "")
        return 
    
    def seed_training_load(self):
        dbutil = BQUtility()    
        
        results = dbutil.get_seed_data()
        for row in results: 
            content = row['content']   
            label = row['label']            
            if len(content) > 0: 
                sentences = re.split(r' *[\.\?!][\'"\)\]]* *', content) 
                for sentence in sentences: 
                    sentence = sentence.strip() + "."
                    if len(sentence) > 4:   
                        catch_stmt = {"sentence" : sentence, "label" : label.lower().strip()}
                        print (">>>>>>> Catch Stmt: ", catch_stmt)
                        dbutil.save_training_data(catch_stmt["sentence"], catch_stmt["label"], "seed", "")
        return

    def import_reports_data(self):    
        filelist = os.listdir(self.reports_folder)   
        for file_name in filelist:  
            if file_name.endswith(".txt"):
                print("Working with ", file_name)
                with open(self.reports_folder + file_name, encoding= "ISO-8859-1") as report_file:
                    filestr = report_file.read()
                    self.dbutil.save_contracts(file_name, filestr, "")
                    #sentences = re.split(r' *[\.\?!][\'"\)\]]* *', filestr)                            
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
                    #print("Statements : ", row[1].rstrip() + ", Label :" + row[0].rstrip())
                    self.dbutil.save_seed_data(keywords, row[0].rstrip(), row[1].rstrip())
                line_count += 1
        csvfile.close()

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