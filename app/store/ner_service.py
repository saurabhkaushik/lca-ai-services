from transformers import AutoTokenizer, pipeline
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer
)
import json

model_path = "dslim/bert-base-NER"
test_data_file = './cuad-data/CUADv12.json'

def prep_data():
    with open(test_data_file) as json_file:
        data = json.load(json_file)

    contract = data['data'][0]['paragraphs'][0]['context']
    return contract

def initialise(): 
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForTokenClassification.from_pretrained(model_path)

    nlp = pipeline('ner', model=model, tokenizer=tokenizer)

    return nlp

def predict(contract, nlp):
    ner_result = nlp(contract)

    return ner_result