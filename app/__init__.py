import logging
import traceback
import time
import os
import requests
from flask import (Flask, flash, jsonify, session, make_response, redirect,
                   render_template, request, url_for)
from flask_cors import CORS
from app.Transformer_Service import Transformer_Service
from app.Risk_Score_Service import Risk_Score_Service
from app.Sentence_Analytics import Sentence_Analytics
from app.Data_ETL_Pipeline import Data_ETL_Pipeline
from app.Model_Testing import Model_Testing

from operator import itemgetter
from app.common.MySQLUtility import MySQLUtility
from app.Highlight_Service import Highlight_Service

def create_app(config, debug=False, testing=False, config_overrides=None):
    apps = Flask(__name__)
    CORS(apps)

    app_env = os.getenv('LCA_APP_ENV')
    if app_env == 'production':
        apps.config.from_object(config.ProductionConfig)
        print('Envornment: ', app_env)
    else: 
        apps.config.from_object(config.DevelopmentConfig)
        print('Envornment: ', app_env)

    apps.debug = debug
    apps.testing = testing
    apps.secret_key = "LCA"  
    
    domains = apps.config['DOMAINS']
    db_host = apps.config['DB_HOST']
    db_user = apps.config['DB_USER']
    db_password = apps.config['DB_PASSWORD']
    db_name = apps.config['DB_NAME']
    mode = apps.config['APP_MODE']

    if config_overrides:
        apps.config.update(config_overrides)

    # Configure logging
    if not apps.testing:
        logging.basicConfig(level=logging.INFO)

    logging.getLogger().setLevel(logging.INFO)

    dbutil = MySQLUtility(db_host, db_user, db_password, db_name)
    highservice = Highlight_Service()
    trans_service = Transformer_Service(dbutil, domains)
    risk_service = Risk_Score_Service(dbutil, domains)
    sent_service = Sentence_Analytics(trans_service, risk_service)

    print ('Creating DB Connection Pool')
    dbutil.get_connection()
    
    print ('Loading AI Models...')
    trans_service.preload_models()

    print ('Loading Keyword Polarity Data...')
    risk_service.load_polarity_data()

    print ('\nAll Pre-Loading Completed. \n')

    @apps.route('/')
    def index():
        return render_template('index.html')

    @apps.route('/contract_new_api', methods=('GET', 'POST'))
    def contract_new_api():
        post = {}
        if request.method == 'POST':
            req_json = request.get_json()
            print (req_json)
            title = req_json['title']
            content = req_json['content']
            domain = req_json['domain']
            threshold = req_json['threshold']
            print("Contract : ", content)
            if not content or not title:
                flash('contract and title is required!')
            else:
                batch_insert = []
                insert_json = {"title": title, "content": content,  "type": "users",
                               "response": '', "domain": domain, "userid": "user"}
                batch_insert.append(insert_json)
                id = dbutil.save_contracts_batch(batch_insert)

                answer = trans_service.process_contract_request(content, domain)

                if answer == None:
                    answer = ''
                response, report_analysis = highservice.highlight_text(answer, threshold)

                post = dbutil.get_contracts_id(id)

                for pst in post:
                    post = pst
                post['highlight_response'] = response
                post['score_report_json'] = report_analysis['score_report_json']
                post['score_context_count_json'] = report_analysis['score_context_count_json']
                post['score_presence_count_json'] = report_analysis['score_presence_count_json']
                post['score_presence_data'] = report_analysis['score_presence_data']
                post['class_analysis_data'] = report_analysis['class_analysis_data']
                #post['class_analysis_key'] = list(report_analysis['class_analysis_data'].keys())
                #post['class_analysis_value'] = list(report_analysis['class_analysis_data'].values())
        print (post)
        json_resp = jsonify(post)
        json_resp.mimetype = 'application/json'
        return json_resp

    @apps.route('/text_analysis_api', methods=('GET', 'POST'))
    def text_analysis_api():
        post = {}
        if request.method == 'POST':
            req_json = request.get_json()
            print (req_json)
            title = req_json['title']
            content = req_json['content']
            domain = req_json['domain']
            print("Contract : ", content)
            if not content or not title:
                flash('contract and title is required!')
            else:
                batch_insert = []
                insert_json = {"title": title, "content": content,  "type": "users",
                               "response": '', "domain": domain, "userid": "user"}
                batch_insert.append(insert_json)
                id = dbutil.save_contracts_batch(batch_insert)

                response = sent_service.process_request(content, domain)

                if not response:
                    response = ''
                
                response = sorted(response, key=itemgetter('c_date'), reverse=False)

                label_total, amount_total = text_analytics_report(response)

                post = dbutil.get_contracts_id(id)

                for pst in post:
                    post = pst

                post['text_analysis_response'] = response
                post['label_total'] = label_total
                post['amount_total'] = amount_total

                print ('Post : ', post)
        json_resp = jsonify(post)
        json_resp.mimetype = 'application/json'
        return json_resp
    
    @apps.route('/training_new_api', methods=('GET', 'POST'))
    def training_new_api():
        if request.method == 'POST':
            req_json = request.get_json()
            print (req_json)
            label = req_json['label']
            content = req_json['content']
            domain = req_json['domain']
            print("Contract : " + content + ' Label:' + label)
            if not content or not label:
                flash('contract and title is required!')
            else:
                batch_insert = []
                insert_json = {"content": content, "label" : label, "type": "users", "eval_label" : "", "eval_score" : 0,
                               "score": 0, "domain": domain, "userid": "user"}
                batch_insert.append(insert_json)
                dbutil.save_training_data_batch(batch_insert)

                print ("New Training added.")
                response = {"id": 0}
                return response
            response = {"id": 0}        
            json_resp = jsonify(response)
            json_resp.mimetype = 'application/json'
            return json_resp

    @apps.route('/seed_data_list_api', methods=('GET', 'POST'))
    def seed_data_list_api():
        req_json = request.get_json()
        print (req_json)
        domain = req_json['domain']
        posts = dbutil.get_seed_data(domain)
        json_resp = jsonify(posts)
        json_resp.mimetype = 'application/json'
        return json_resp
    
    @apps.route('/contract_list_api', methods=('GET', 'POST'))
    def contract_list_api():
        req_json = request.get_json()
        print (req_json)
        domain = req_json['domain']
        posts = dbutil.get_contracts(domain)
        json_resp = jsonify(posts)
        json_resp.mimetype = 'application/json'
        return json_resp

    def text_analytics_report(response):
        label_total = {}
        amount_total = {}
        amount_total['total'] = 0
        for sent_dict in response:
            if 'c_money' in sent_dict.keys():
                amount_total['total'] += int(sent_dict['c_money']) * int(sent_dict['polarity'])
                if sent_dict['label'] in label_total.keys(): 
                    label_total[sent_dict['label']] += int(sent_dict['c_money']) * int(sent_dict['polarity'])
                else: 
                    label_total[sent_dict['label']] = int(sent_dict['c_money']) * int(sent_dict['polarity'])
        print('Label Total : ', label_total)
        return label_total, amount_total 

    @apps.route('/training_service', methods=('GET', 'POST'))
    def training_service():
        req_json = request.get_json()
        print (req_json)
        domain = req_json['domain']
        trans_service.train_model(domain)
        return render_template('index.html')

    @apps.route('/model_test_service', methods=('GET', 'POST'))
    def model_test_service():
        contract = "This is a very legalised way of doing businesss."
        answer_results = {}
        for domain in domains:
            answer_results = trans_service.process_contract_request(contract, domain)
            print("Contract Analysis : ", answer_results)
        return jsonify(answer_results)
    
    @apps.route('/etl_service', methods=('GET', 'POST'))
    def etl_service():
        data_etl = Data_ETL_Pipeline(dbutil, domains, mode)
        data_etl.start_process()
        return render_template('index.html')
    
    @apps.route('/db_service', methods=('GET', 'POST'))
    def db_service():
        data_etl = Data_ETL_Pipeline(dbutil, domains, mode)
        data_etl.create_dataset()
        return render_template('index.html')

    @apps.route('/model_accuracy', methods=('GET', 'POST'))
    def model_accuracy():
        data_test = Model_Testing(dbutil, domains, mode)
        results = data_test.start_testing()
        return jsonify(results)

    @apps.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    @apps.errorhandler(500)
    def server_error(e):
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

    return apps
