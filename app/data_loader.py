from app.BQUtility import BQUtility
import json 
import csv

class data_loader: 
    def __init__(self) -> None:
        pass

    dbutil = BQUtility()
    cuda_data_file = './cuad-data/CUADv1.json'
    keywords_data_file = './cuad-data/keywords.txt'
    statements_data_file = './cuad-data/statements.txt'
    seed_data_file = './cuad-data/seed_data.csv'

    def prep_contract_data(self):
        with open(self.cuda_data_file) as json_file:
            data = json.load(json_file)
        for data_row in data['data']:
            contract = data_row['paragraphs'][0]['context']
            title = data_row['title']
            self.dbutil.save_contracts(title, contract, "")
        return 

    def import_seed_data(self):
        
        with open(self.seed_data_file, newline='', encoding='utf-8') as csvfile:
            seedreader = csv.reader(csvfile)
            line_count = 0
            for row in seedreader:
                if line_count >0:
                    print(row[1].rstrip() + ", " + row[0].rstrip())
                    self.dbutil.save_learndb("", row[1].rstrip(), row[0].rstrip())
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