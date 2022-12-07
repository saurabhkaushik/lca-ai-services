import logging
import os

from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from flask import make_response, jsonify
from app.Transformer_Classifier import Transformer_Classifier
from app.common.MySQLUtility import MySQLUtility
from app.common.GCP_Storage import GCP_Storage
from app.Data_ETL_Pipeline import Data_ETL_Pipeline
from app.Risk_Score_Service import Risk_Score_Service

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
    
    if config_overrides:
        apps.config.update(config_overrides)

    # Configure logging
    if not apps.testing:
        logging.basicConfig(level=logging.INFO)

    logging.getLogger().setLevel(logging.INFO)

    dbutil = MySQLUtility(db_host, db_user, db_password, db_name)
    class_service = Transformer_Classifier(dbutil, domains)
    risk_scorer = Risk_Score_Service(dbutil, domains)
    gcp_store = GCP_Storage(domains, storage_bucket_env)

    print ('Loading DB Connection Pool...')
    dbutil.get_connection()

    print ('Loading AI Models...')
    class_service.preload_models()

    print ('Loading Keyword Polarity Data...')
    risk_scorer.load_polarity_data()

    print ('Setting up Storage Bucket...')
    gcp_store.setup_bucket()

    if data_env == 'cloud': 
        print ('Updating Model from initialization.')        
        gcp_store.download_models()
    
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
        response = class_service.process_contract_request(contract, domain)
        dbutil.update_contracts_id(contract_id, contract_data['title'], contract, str(response))
        json_response = jsonify(response)
        print("Response : \n", response)
        return json_response

    @apps.route('/training_service', methods=('GET', 'POST'))
    def training_service():
        for domain in domains:
            class_service.prepare_train_dataset(domain)
            class_service.training(domain)
        return render_template('index.html')
    
    @apps.route('/etl_service', methods=('GET', 'POST'))
    def etl_service():
        data_etl = Data_ETL_Pipeline(dbutil, domains)
        data_etl.start_process()
        return render_template('index.html')
    
    @apps.route('/get_seed_service', methods=('GET', 'POST'))
    def get_seed_service():
        store_util = GCP_Storage(domains, storage_bucket_env)
        store_util.download_seed_data()
        return render_template('index.html')
    
    @apps.route('/get_model_service', methods=('GET', 'POST'))
    def get_model_service():
        store_util = GCP_Storage(domains, storage_bucket_env)
        store_util.download_models()
        return render_template('index.html')
    
    @apps.route('/put_model_service', methods=('GET', 'POST'))
    def put_model_service():
        store_util = GCP_Storage(domains, storage_bucket_env)
        store_util.upload_models()
        return render_template('index.html')

    @apps.route('/model_test_service', methods=('GET', 'POST'))
    def model_test_service():
        contract = "This is a very legalised way of doing businesss."
        answer_results = {}
        for domain in domains:
            answer_results = class_service.process_contract_request(contract, domain)
            print("Contract Analysis : ", answer_results)
        return jsonify(answer_results)

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
