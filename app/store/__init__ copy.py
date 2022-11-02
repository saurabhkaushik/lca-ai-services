import sqlite3, logging

from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort   
from flask import make_response, jsonify
import app.store.qna_service, app.ner_service, app.highlight_service, app.classify_service

def create_app(config, debug=False, testing=False, config_overrides=None):
    apps = Flask(__name__)
    apps.config.from_object(config)
    apps.debug = debug
    apps.testing = testing

    nlp_qna = "" # app.qna_service.initialise()
    nlp_ner = "" # app.ner_service.initialise()
      
    article_text = app.highlight_service.load_data()
    app.highlight_service.generate_training_corpus(article_text)  

    train_hg, valid_hg = app.classify_service.prepare_train_valid_df()
    model = app.classify_service.training(train_hg, valid_hg) 
    article_text = app.classify_service.load_data()

    if config_overrides:
        apps.config.update(config_overrides)

    # Configure logging
    if not apps.testing:
        logging.basicConfig(level=logging.INFO)
    
    logging.getLogger().setLevel(logging.INFO)

    def get_db_connection():
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_learning():
        conn = get_db_connection()
        posts = conn.execute('SELECT * FROM learndb').fetchall()
        conn.close()
        return posts

    @apps.route('/')
    def index():
        posts = ""
        return render_template('index.html', posts=posts)

    @apps.route('/highlight_service', methods=('GET', 'POST'))
    def highlight_service():  
        request_data = request.get_json() 
        contract = request_data['contract']
        print("contract : ", contract)
        if not contract: 
            flash('contract is required!')
            return
        answer_results = app.highlight_service.process_paragraph(contract, model)
        answer_results = app.highlight_service.highlight_ranking(answer_results)
        print("answer_results : ", answer_results)
        return jsonify(answer_results)

    @apps.route('/classify_service', methods=('GET', 'POST'))
    def classify_service():  
        request_data = request.get_json() 
        contract = request_data['content']
        print("contract : ", contract)
        if not contract: 
            flash('contract is required!')
            return
        answer_results = app.classify_service.process_paragraph(contract, model)
        answer_results = app.classify_service.highlight_ranking(answer_results)
        print("answer_results : ", answer_results)
        return jsonify(answer_results)

    @apps.route('/qna_predict', methods=('GET', 'POST'))
    def qna_predict():  
        request_data = request.get_json() 
        contract = request_data['contract']
        question = request_data['question']
        print("contract : ", contract)
        print("question : ", question)
        if not question:
            flash('question is required!')
            return
        if not contract: 
            flash('contract is required!')
            return
        answer_results = app.store.qna_service.predict(question, contract, nlp_qna)
        print("answer_results : ", answer_results)
        return jsonify(answer_results)

    @apps.route('/ner_predict', methods=('GET', 'POST'))
    def ner_predict():  
        request_data = request.get_json() 
        contract = request_data['contract']
        print("contract : ", contract)
        if not contract: 
            flash('contract is required!')
            return
        ner_results = app.ner_service.predict(contract, nlp_ner)
        print("ner_results: ", str(ner_results))
        return jsonify(str(ner_results))

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
