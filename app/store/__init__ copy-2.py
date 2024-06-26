import logging
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort   
from flask import make_response, jsonify

from app.classify_service import classify_service as Classify_Service
from app.DBUtility import DBUtility
from app.BQUtility import BQUtility
from app.highlight_service import highlight_service

def create_app(config, debug=False, testing=False, config_overrides=None):
    apps = Flask(__name__)
    apps.config.from_object(config)
    apps.debug = debug
    apps.testing = testing

    class_service = Classify_Service()
    dbutil = BQUtility() 
    #dbutil = DBUtility() 
    high_service = highlight_service()   
    dbutil.create_database() 

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
        contract = request_data['content']
        print("Contract Detail : ", contract)
        if not contract: 
            flash('contract is required!')
            return
        answer_results = class_service.process_contract(contract)
        answer_results = high_service.highlight_ranking(answer_results)
        print("Contract Analysis : ", answer_results)
        return jsonify(answer_results)

    @apps.route('/training_service', methods=('GET', 'POST'))
    def training_service():  
        statmt = dbutil.get_learndb()
        keywords = set()
        statements = []
        for row in statmt:
            t_sentence = [c_word.strip().lower() for c_word in row['keywords'].split(',') if len(c_word) > 0]
            if len(t_sentence) > 0:
                keywords.update(t_sentence)
            statements.append(row['statements'])
        keywords = set(keywords)

        #verb_list = high_service.extract_keywords(statements)        
        #keywords.update(verb_list)

        print("Keywords : ", keywords)
        print("Statements : ", statements)
        
        high_service.generate_training_corpus(keywords, statements)  

        train_hg, valid_hg = class_service.prepare_train_dataset()
        model = class_service.training(train_hg, valid_hg)         
        return render_template('index.html')
    
    @apps.route('/test_service', methods=('GET', 'POST'))
    def test_service():  
        contract = "This is a very legalised way of doing businesss."
        answer_results = class_service.process_contract(contract)
        answer_results = high_service.highlight_ranking(answer_results)
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
