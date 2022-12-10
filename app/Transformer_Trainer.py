import logging
from os.path import exists

import pandas as pd
import pyarrow as pa
from datasets import Dataset
from sklearn.model_selection import train_test_split
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          Trainer, TrainingArguments, pipeline)


model_checkpoint = "distilbert-base-uncased"

class Transformer_Trainer(object):
    label_y = dict()
    label_x = dict()
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
    dbutil = None 
    train_hg = None
    valid_hg = None
    mode = None
    model = None
    trainer = None

    def __init__(self, dbutil):
        self.dbutil = dbutil
        pass

    def process_data(self, row):
        text = row['content']
        text = str(text)
        text = ' '.join(text.split())
        encodings = self.tokenizer(text, padding="max_length",
                              truncation=True, max_length=128)

        label = self.label_y[row['label'].lower().strip()]

        encodings['label'] = label
        encodings['text'] = text

        return encodings

    def prepare(self, domain):
        processed_data = []        
        train_data1 = self.dbutil.get_training_data(domain)
        train_data2 = self.dbutil.get_training_data(domain)

        label_count = 0
        for row in train_data1:
            key = row["label"].lower().strip()
            if not key in self.label_y.keys():
                self.label_y.update({key: label_count})
                self.label_x.update({label_count: key})
                label_count += 1
        
        for row in train_data2:
            processed_data.append(self.process_data(row))

        new_df = pd.DataFrame(processed_data)
        if not len(new_df) > 0:
            logging.exception("Data Empty")
            return 
            
        train_df = None 
        valid_df = None
        try: 
            train_df, valid_df = train_test_split(
                new_df,
                test_size=0.2,
                random_state=2022
            )
        except Exception as e: 
            logging.exception("Data Empty")
            return

        self.train_hg = Dataset(pa.Table.from_pandas(train_df))
        self.valid_hg = Dataset(pa.Table.from_pandas(valid_df))
        return 

    def train(self, model_folder):
        if self.train_hg == None:
            logging.error('Data is empty')
            return
        training_args = TrainingArguments(
            output_dir="./result", evaluation_strategy="epoch")
        id2label = self.label_x
        label2id = {val: key for key, val in id2label.items()}
        num_labels = len(id2label)

        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_checkpoint, num_labels=num_labels, id2label=id2label, label2id=label2id)

        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_hg,
            eval_dataset=self.valid_hg,
            tokenizer=self.tokenizer
        )
        self.trainer.train()   
        self.model.save_pretrained(model_folder)     
        return self.model

    def predict(self, sentences, model_folder):
        model = AutoModelForSequenceClassification.from_pretrained(model_folder)
        classifier = None
        try: 
            classifier = pipeline("text-classification",
                                model=model, tokenizer=self.tokenizer)
        except Exception as e:
            logging.exception('Model missing :')
            return None

        results = classifier(sentences)
        return results

    def predict_model(self, sentences, model):
        classifier = None
        try: 
            classifier = pipeline("text-classification",
                                model=model, tokenizer=self.tokenizer)
        except Exception as e:
            logging.exception('Model missing :')
            return None

        results = classifier(sentences)
        return results

    def evalute(self, domain):
        metrics = self.trainer.evaluate()
        print("Metrics : ", metrics)
