
import json 
from app.common.MySQLUtility import MySQLUtility
from app.Transformer_Service import Transformer_Service
testing_folder = '.testing/'
test_case_file = testing_folder + 'test_data.json'
result_file = testing_folder + 'test_results.json'

class Model_Testing(object):
    dbutil = None
    data_load = None
    textrank = None 
    key_classifier = None
    class_service = None
    risk_class = None
    domains = None
    classes = ['current liabilities', 'contingent liabilities', 'non-current liabilities', 'NA']

    def __init__(self, dbutil, domains, mode):
        self.dbutil = dbutil
        self.domains = domains
        self.class_service = Transformer_Service(self.dbutil, domains, mode)
        pass   

    def model_testing(self): 
        with open(test_case_file) as json_file:
            data = json.load(json_file)
        results = []
        for domain in self.domains:
            test_data = data[domain]        
            for test in test_data: 
                result = {}
                text = test['data']
                label = test['label']
                response = self.class_service.process_contract_request(text, domain)
                if response:
                    result['text'] = text
                    result['a_label'] = label
                    result['p_label'] = response[0]['label']
                    result['p_score'] = response[0]['presence_score']
                    result['match'] = True if result['a_label'] == result['p_label'] else False
                    results.append(result)
        return results
    
    def result_analysis(self, results):
        analysis = {}
        for a_class in self.classes: 
            analysis[a_class] = {'count': 0, 'match': 0}

        for result in results: 
            for a_class in self.classes:                 
                if a_class == result['a_label']:
                    analysis[a_class]['count'] += 1
                    if result['match'] == True:
                        analysis[a_class]['match'] += 1
        return analysis
        
    def start_testing(self):
        results = self.model_testing()
        print('Results: \n', results)
        analysis = self.result_analysis(results)
        print('\nAnalysis: \n', analysis)

        result_dict = {"results" : results, "analysis" : analysis}
        json_object = json.dumps(result_dict, indent=4)

        with open(result_file, "w") as outfile:
            outfile.write(json_object)
        return json_object