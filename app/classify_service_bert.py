from transformers import AutoModelForSequenceClassification
from transformers import BertForSequenceClassification
import json 
from transformers import AutoTokenizer
from transformers import pipeline
from sklearn.model_selection import train_test_split
import pandas as pd
import pyarrow as pa
from datasets import Dataset
from sklearn import preprocessing
from transformers import TrainingArguments, Trainer
import re
from app.BQUtility import BQUtility

from app.highlight_service import highlight_service

model_checkpoint = "facebook/bart-large-mnli" # "distilbert-base-uncased"
classification = "zero-shot-classification" # "text-classification"

class classify_service_bert:

    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    high_service = highlight_service()
    dbutil = BQUtility()

    label_y = dict()
    label_x = dict()

    def __init__(self) -> None:
        pass

    def process_data(self, row):
        text = row['content']
        text = str(text)
        text = ' '.join(text.split())

        encodings = self.tokenizer(text, padding="max_length", truncation=True, max_length=128)

        label = self.label_y[row['label'].lower().strip()]

        encodings['label'] = label
        encodings['text'] = text

        return encodings

    def prepare_train_dataset(self, type="all"): 
        processed_data = []    
        train_data = self.dbutil.get_training_data(type)
        
        label_count = 0
        for row in train_data:        
            key = row["label"].lower().strip()
            if not key in self.label_y.keys():
                self.label_y.update({key : label_count})
                self.label_x.update({label_count : key})
                label_count += 1
        
        train_data = self.dbutil.get_training_data(type)
        for row in train_data:  
            processed_data.append(self.process_data(row))
            
        new_df = pd.DataFrame(processed_data)

        train_df, valid_df = train_test_split(
            new_df,
            test_size=0.1,
            random_state=2022
        )

        train_hg = Dataset(pa.Table.from_pandas(train_df))
        valid_hg = Dataset(pa.Table.from_pandas(valid_df))
        return train_hg, valid_hg

    def training(self, train_hg, valid_hg):
        training_args = TrainingArguments(output_dir="./result", evaluation_strategy="epoch")
        id2label = self.label_x
        label2id = {val: key for key, val in id2label.items()}
        num_labels = len(id2label)

        model = BertForSequenceClassification.from_pretrained(
            model_checkpoint, num_labels=num_labels, id2label=id2label, label2id=label2id, ignore_mismatched_sizes=True)  

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_hg,
            eval_dataset=valid_hg,
            tokenizer=self.tokenizer
        )
        trainer.train()
        metrics = trainer.evaluate()
        print("Metrics : " , metrics)
        model.save_pretrained('./model/')
        return model

    def predict(self, sentences, model): 
        # model = AutoModelForSequenceClassification.from_pretrained('./model/')
        classifier = pipeline(classification, model=model, tokenizer=self.tokenizer)
        print ("sentences : ", sentences)
        try: 
            results = classifier(sentences)
            return results 
        except TypeError: 
            print ("Error due to sentences : ", sentences)
        return None 

    def process_contract(self, article_text):
        model = BertForSequenceClassification.from_pretrained('./model/')
        return_value = {}
        for c_sentence in article_text.split('.'):
            results = self.predict(c_sentence, model)
            if results:
                score = (results[0]["score"]  * 100)
                try: 
                    res = re.search(c_sentence, article_text) # TODO Revisite 
                    if res:
                        stmt_index = str(res.start()) + "-" + str(res.end())
                        relevence = score
                        return_value[stmt_index] = {"start_index" : res.start(), "end_index" : res.end(), "relevence" : relevence}
                except IndexError:
                    print()

        return return_value

    def contract_training_data(self):
        model = AutoModelForSequenceClassification.from_pretrained('./model/')
        dbutil = BQUtility()
        results = dbutil.get_contracts()
        for row in results:
            article_text = row["content"]
            for c_sentence in article_text.split('.'):
                results = self.predict(c_sentence, model)
                if results:
                    score = (results[0]["score"]  * 100)   
                    label = results[0]["label"]
                            
                    if score > 9:
                        print ("Sentences : ", c_sentence)
                        print ("Result : ", label)
                        print ("Score : ", score)   
                        dbutil.save_training_data(c_sentence, label, "generated", "")

        return 



