import logging
import os

from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from flask import make_response, jsonify
from app.Transformer_Classifier import Transformer_Classifier
from app.MySQLUtility import MySQLUtility
from app.Risk_Score_Service import Risk_Score_Service
from app.PreProcessText import PreProcessText

def create_app(config, debug=False, testing=False, config_overrides=None):
    apps = Flask(__name__)
    apps.config.from_object(config.DevelopmentConfig)
    apps.debug = debug
    apps.testing = testing

    domains = apps.config['DOMAINS']
    google_cert_key = apps.config['GOOGLE_CERT_KEY']
    db_host = apps.config['DB_HOST']
    db_user = apps.config['DB_USER']
    db_password = apps.config['DB_PASSWORD']

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_cert_key

    dbutil = MySQLUtility(db_host, db_user, db_password)
    class_service = Transformer_Classifier(dbutil)

    if config_overrides:
        apps.config.update(config_overrides)

    # Configure logging
    if not apps.testing:
        logging.basicConfig(level=logging.INFO)

    logging.getLogger().setLevel(logging.INFO)

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
        model = class_service.load_model(domain)
        response = class_service.process_contract_request(contract, model)
        #dbutil.update_contracts_id(contract_id, contract_data['title'], contract, str(response))
        json_response = jsonify(response)
        print("Response : \n", response)
        return json_response

    @apps.route('/training_service', methods=('GET', 'POST'))
    def training_service():
        for domain in domains:
            class_service.training(domain)
        return render_template('index.html')

    @apps.route('/test_service', methods=('GET', 'POST'))
    def test_service():
        contract = "This is a very legalised way of doing businesss."
        domain = "Liabilities"
        model = class_service.load_model(domain)
        answer_results = class_service.process_contract_request(
            contract, model)
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
