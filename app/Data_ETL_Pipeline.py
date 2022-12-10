from app.Transformer_Service import Transformer_Service

from app.Data_Loader import Data_Loader
from app.TextRank_Extractor import TextRank_Extractor
from app.Keyword_Classifier import Keyword_Classifier
from app.common.MySQLUtility import MySQLUtility
from app.Risk_Score_Service import Risk_Score_Service

class Data_ETL_Pipeline(object):
    dbutil = None
    data_load = None
    textrank = None 
    key_classifier = None
    domains = []
    risk_class = None
    mode = None

    def __init__(self, dbutil, domains, mode):
        self.dbutil = dbutil
        self.domains = domains
        self.mode = mode
        self.data_load = Data_Loader(self.dbutil)
        self.textrank = TextRank_Extractor(self.dbutil)
        self.key_classifier = Keyword_Classifier(self.dbutil)      
        self.risk_class = Risk_Score_Service(self.dbutil, self.domains)    
        self.model_service = Transformer_Service(dbutil, domains)    
        pass   

    def create_dataset(self):
        print ('\n******* create_dataset\n')
        print("dbutil.db_cleanup():")
        self.dbutil.clean_db()
        print("dbutil.create_database():")
        self.dbutil.create_database() 

    def load_file_data(self): 
        print ('\n******* load_file_data\n')
        print("data_load.import_seed_data_batch():")
        self.data_load.import_seed_data_batch()

        if self.mode == 'learning':
            for domain in self.domains:
                print("self.data_load.import_reports_contract_data()" + domain)
                self.data_load.import_reports_contract_data(domain)

    def process_seed_training_data(self):
        print ('\n******* process_seed_training_data\n')
        for domain in self.domains:
            print("textrank.extract_keyword_seed_data():" + domain)
            self.textrank.extract_keyword_seed_data(domain) 

            print("textrank.load_seed_to_training_data_batch():" + domain)
            self.data_load.load_seed_to_training_data_batch(domain) 

    def process_keyword_model(self):
        print ('\n******* process_keyword_model\n')
        if self.mode == 'learning':
            for domain in self.domains:
                print("model_service.train_model():" + domain)
                self.model_service.train_model(domain)

                print("model_service.process_contract_data():" + domain)
                self.model_service.process_contract_data(domain)

    def process_transformer_model(self):
        print ('\n******* process_transformer_model\n')
        for domain in self.domains:
            print("model_service.train_model():" + domain)
            self.model_service.train_model(domain)

            print("risk_class.process_keyword_polarity():" , domain)
            self.risk_class.process_keyword_polarity(domain)

    def evaluate_results(self):
        print ('\n******* evaluate_results\n')
        if self.mode == 'learning':
            for domain in self.domains:
                print("class_service.process_contract_training_data_eval():" + domain)
                self.model_service.process_contract_training_data_eval(domain)

    def start_process(self):
        self.create_dataset()
        self.load_file_data()
        self.process_seed_training_data() 
        self.process_keyword_model()
        self.process_transformer_model()
        #self.evaluate_results()