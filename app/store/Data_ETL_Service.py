from app.Transformer_Classifier import Transformer_Classifier 
from app.Data_Loader import Data_Loader
from app.TextRank_Extractor import TextRank_Extractor
from app.Keyword_Classifier import Keyword_Classifier
from app.MySQLUtility import MySQLUtility
from flask import Blueprint

data_loader_service = Blueprint('data_loader_service', __name__)

@data_loader_service.route("")
    dbutil = None
    data_load = None
    textrank = None 
    key_classifier = None
    class_service = None
    domains = []

        self.dbutil = dbutil
        self.domains = domains
        self.data_load = Data_Loader(self.dbutil)
        self.textrank = TextRank_Extractor(self.dbutil)
        self.key_classifier = Keyword_Classifier(self.dbutil)
        self.class_service = Transformer_Classifier(self.dbutil)
        pass    

def create_dataset(self):
    print("dbutil.db_cleanup():")
    self.dbutil.clean_db()
    print("dbutil.create_database():")
    self.dbutil.create_database() 

def load_seed_training_data(self):
    print("data_load.import_seed_data_batch():")
    self.data_load.import_seed_data_batch()

    for domain in self.domains:
        print("textrank.extract_keyword_seed_data():" + domain)
        self.textrank.extract_keyword_seed_data(domain) 

        print("textrank.load_seed_to_training_data_batch():" + domain)
        self.data_load.load_seed_to_training_data_batch(domain) 

def load_contract_data(self):
    for domain in self.domains:
        print("self.data_load.import_reports_contract_data()" + domain)
        self.data_load.import_reports_contract_data(domain)

def process_keyword_model(self):
    for domain in self.domains:
        print("key_classifier.prepare_training_data():" + domain)
        self.key_classifier.prepare_training_data(domain)

        print("key_classifier.train_model():" + domain)
        self.key_classifier.train_model(domain)

        print("key_classifier.evaluate_model():" + domain)
        self.key_classifier.evaluate_model(domain)

        print("key_classifier.process_contract_data():" + domain)
        self.key_classifier.process_contract_data(domain)

def process_transformer_model(self):
    for domain in self.domains:
        print("class_service.training():" + domain)
        self.class_service.training(domain)    

        print("class_service.process_contract_training_data_eval():" + domain)
        self.class_service.process_contract_training_data_eval(domain)

def evaluate_results(self):
    for domain in self.domains:
        print ("key_classifier.Keyword Classifier Accuracy: " + domain)
        self.key_classifier.evaluate_model(domain) 
        
        print ("class_service.Transformer Classifier Accuracy: " + domain)
        self.class_service.evalute_model(domain)