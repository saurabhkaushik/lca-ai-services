import app.highlight_service as highlight_service
#import app.ner_service as ner_service 

def main(): 
    '''
    #question, contract = qna_service.prep_data()
    #tokenizer, nlp = qna_service.initialise()
    #qna_result = qna_service.predict(question[0], contract, tokenizer, nlp)
    #print(qna_result)
    contract = ner_service.prep_data()
    nlp = ner_service.initialise()
    ner_result = ner_service.predict(contract, nlp)
    print(ner_result)
    '''
    contract = highlight_service.prep_data()
    result = highlight_service.highlight_sentences(contract)
    print(result)

if __name__ == "__main__":
    main()