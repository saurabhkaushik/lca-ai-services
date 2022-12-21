import logging
import os

from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from flask import make_response, jsonify
from app.Transformer_Service import Transformer_Service
from app.common.MySQLUtility import MySQLUtility
from app.common.GCP_Storage import GCP_Storage
from app.Data_ETL_Pipeline import Data_ETL_Pipeline
from app.Risk_Score_Service import Risk_Score_Service
from app.Model_Testing import Model_Testing
from app.Sentence_Analytics import Sentence_Analytics

def create_app(config, debug=False, testing=False, config_overrides=None):
    apps = Flask(__name__)

    app_env = os.getenv('LCA_APP_ENV')
    if app_env == 'production':
        apps.config.from_object(config.ProductionConfig)
        print('Envornment: ', app_env)
    else: 
        apps.config.from_object(config.DevelopmentConfig)
        print('Envornment: ', app_env)

    apps.debug = debug
    apps.testing = testing

    domains = apps.config['DOMAINS']
    db_host = apps.config['DB_HOST']
    db_user = apps.config['DB_USER']
    db_password = apps.config['DB_PASSWORD']
    db_name = apps.config['DB_NAME']
    data_env = apps.config['DATA_ENV']
    storage_bucket_env = apps.config['STORAGE_BUCKET']
    mode = apps.config['APP_MODE']
    print('DB Name: ', db_name)
    print('App Mode: ', mode)
    print('Data Env: ', data_env)
    print('GCP Storage: ', storage_bucket_env)
    
    if config_overrides:
        apps.config.update(config_overrides)

    # Configure logging
    if not apps.testing:
        logging.basicConfig(level=logging.INFO)

    logging.getLogger().setLevel(logging.INFO)

    dbutil = MySQLUtility(db_host, db_user, db_password, db_name)
    trans_service = Transformer_Service(dbutil, domains)
    risk_service = Risk_Score_Service(dbutil, domains)
    gcp_service = GCP_Storage(domains, storage_bucket_env, mode)
    sent_service = Sentence_Analytics(trans_service, risk_service)

    print ('Loading DB Connection Pool...')
    dbutil.get_connection()

    print ('Loading AI Models...')
    trans_service.preload_models()

    print ('Loading Keyword Polarity Data...')
    risk_service.load_polarity_data()

    print ('Setting up Storage Bucket...')
    gcp_service.setup_bucket()

    if data_env == 'cloud': 
        print ('Updating Model from initialization.')        
        gcp_service.download_models()
    
    print ('\nAll Pre-Loading Completed. \n')

    @apps.route('/')  
    def index():
        posts = ""
        return render_template('index.html', posts=posts)

    @apps.route('/classify_service', methods=('GET', 'POST'))
    def classify_service():
        request_data = request.get_json()
        contract_id = request_data['id']
        domain = request_data['domain']
        print("Contract Id : ", contract_id)
        if not contract_id:
            flash('contract id is required!')
            return None
        results = dbutil.get_contracts_id(contract_id)
        for rows in results:
            contract_data = rows
        contract = contract_data['content'] 
        #contract = preprocess.clean_input_text(contract)    
        print('Contract : \n', contract)
        response = trans_service.process_contract_request(contract, domain)
        dbutil.update_contracts_id(contract_id, contract_data['title'], contract, str(response))
        json_response = jsonify(response)
        print("Response : \n", response)
        return json_response

    @apps.route('/text_analysis_service', methods=('GET', 'POST'))
    def text_analysis_service():
        request_data = request.get_json()
        contract_id = request_data['id']
        domain = request_data['domain']
        print("Contract Id : ", contract_id)
        if not contract_id:
            flash('contract id is required!')
            return None
        results = dbutil.get_contracts_id(contract_id)
        for rows in results:
            contract_data = rows
        contract = contract_data['content'] 
        print('Contract : \n', contract)
        response = sent_service.process_request(contract, domain)
        json_response = jsonify(response)
        print("Response : \n", response)
        return json_response

    @apps.route('/training_service', methods=('GET', 'POST'))
    def training_service():
        for domain in domains:
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
    
    @apps.route('/get_model_service', methods=('GET', 'POST'))
    def get_model_service():
        gcp_service.download_models()
        return render_template('index.html')
    
    @apps.route('/put_model_service', methods=('GET', 'POST'))
    def put_model_service():
        gcp_service.upload_models()
        return render_template('index.html')
    
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
