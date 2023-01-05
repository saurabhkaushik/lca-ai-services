from transformers import AutoTokenizer, pipeline
from transformers import (
    AutoConfig,
    AutoModelForQuestionAnswering,
    AutoTokenizer
)
import json

model_path = 'cuad-models/roberta-base/'
question = "NULL"

def prep_data():
    with open('./cuad-data/CUADv12.json') as json_file:
        data = json.load(json_file)
    questions = []
    for i, q in enumerate(data['data'][0]['paragraphs'][0]['qas']):
        question = data['data'][0]['paragraphs'][0]['qas'][i]['question']
        questions.append(question)
    contract = data['data'][0]['paragraphs'][0]['context']
    return questions, contract

def initialise(): 
    config_class, model_class, tokenizer_class = (
        AutoConfig, AutoModelForQuestionAnswering, AutoTokenizer)
    config = config_class.from_pretrained(model_path)
    tokenizer = tokenizer_class.from_pretrained(
        model_path, do_lower_case=True, use_fast=False)
    model = model_class.from_pretrained(model_path, config=config)

    tokenizer.encode(question, truncation=True, padding=True)

    nlp = pipeline('question-answering', model=model, tokenizer=tokenizer)
    return nlp

def predict(question, contract, nlp):

    answerResp = nlp({
        'question' : question, 
        'context': contract 
    })

    return answerResp['answer']
