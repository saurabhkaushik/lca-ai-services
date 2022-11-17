import logging
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort   
from flask import make_response, jsonify

from app.Transformer_Classifier import Transformer_Classifier 
from app.MySQLUtility import MySQLUtility
from app.Risk_Score_Service import Risk_Score_Service

score_service = Risk_Score_Service()   
class_service = Transformer_Classifier()
dbutil = MySQLUtility() 

def create_app(config, debug=False, testing=False, config_overrides=None):
    apps = Flask(__name__)
    apps.config.from_object(config)
    apps.debug = debug
    apps.testing = testing

    #dbutil.create_database() 
    model = class_service.load_model()

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
        print("Contract Id : ", contract_id)
        if not contract_id: 
            flash('contract id is required!')
            return None
        results = dbutil.get_contracts_id(contract_id)
        for rows in results:
            contract_data = rows
        print ('Contract : ', contract_data)
        contract = contract_data['content']
        answer_results = class_service.process_contract_request(contract, model)
        response = score_service.highlight_ranking(answer_results)
        
        #dbutil.update_contracts_id(contract_id, contract_data['title'], contract, str(response))
        json_response = jsonify(response)
        print("Response : ", response)
        return json_response

    @apps.route('/training_service', methods=('GET', 'POST'))
    def training_service():  
        train_hg, valid_hg = class_service.prepare_train_dataset()
        model = class_service.training(train_hg, valid_hg)         
        return render_template('index.html')
    
    @apps.route('/test_service', methods=('GET', 'POST'))
    def test_service():  
        contract = "This is a very legalised way of doing businesss."
        answer_results = class_service.process_contract_request(contract)
        answer_results = score_service.highlight_ranking(answer_results)
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
