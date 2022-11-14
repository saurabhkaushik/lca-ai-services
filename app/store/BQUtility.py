from google.cloud import bigquery
from google.cloud.exceptions import NotFound, Conflict
import os
from google.api_core.exceptions import BadRequest
import uuid

class BQUtility:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './store/genuine-wording-key.json'
    project_id = "genuine-wording-362504"
    dataset_id = "{}.lca_db".format(project_id)
    table_id1 = "genuine-wording-362504.lca_db.contract_data"
    table_id2 = "genuine-wording-362504.lca_db.seed_data"
    table_id3 = "genuine-wording-362504.lca_db.training_data"

    client = bigquery.Client(project=project_id)

    def __init__(self) -> None:
        pass

    def create_database(self):
        dataset = bigquery.Dataset(self.dataset_id)
        dataset.location = "US"

        try:
            dataset = self.client.create_dataset(dataset, timeout=30)
        except Conflict:
            print('Dataset %s already exists, not creating.', dataset.dataset_id)
        else:
            print('Dataset %s successfully created.', dataset.dataset_id)

        schema_contract_data = [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("content", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("type", "STRING", mode="NULLABLE"), # curated, users
            bigquery.SchemaField("response", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("domain", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("userid", "STRING", mode="NULLABLE")
        ]

        schema_seed_data = [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("keywords", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("content", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("type", "STRING", mode="NULLABLE"), # curated, users 
            bigquery.SchemaField("label", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("domain", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("userid", "STRING", mode="NULLABLE")
        ]

        schema_training_data = [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("content", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("type", "STRING", mode="NULLABLE"),  # seed, contract  
            bigquery.SchemaField("label", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("eval_label", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("score", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("eval_score", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("domain", "STRING", mode="NULLABLE")
        ]

        try:
            table1 = bigquery.Table(self.table_id1, schema=schema_contract_data)
            table1 = self.client.create_table(table1)  
        except Conflict: 
            print('Table %s already exists, not creating.', table1.table_id)
        else:
            print('Table %s successfully created.', table1.table_id)

        try: 
            table2 = bigquery.Table(self.table_id2, schema=schema_seed_data)
            table2 = self.client.create_table(table2)  # Make an API request.
        except Conflict: 
            print('Table %s already exists, not creating.', table2.table_id)
        else:
            print('Table %s successfully created.', table2.table_id)

        try: 
            table3 = bigquery.Table(self.table_id3, schema=schema_training_data)
            table3 = self.client.create_table(table3)  # Make an API request.
        except Conflict: 
            print('Table %s already exists, not creating.', table3.table_id)
        else:
            print('Table %s successfully created.', table3.table_id)

    def db_cleanup(self):
        self.client.delete_table(self.table_id1, not_found_ok=True)
        self.client.delete_table(self.table_id2, not_found_ok=True)
        self.client.delete_table(self.table_id3, not_found_ok=True)
        print('Deleted all three tables.')
        #self.client.delete_dataset(self.dataset_id, delete_contents=True, not_found_ok=True)
        #print("Deleted dataset '{}'.".format(self.dataset_id))

    # Contracts CRUD 
    def get_contracts(self, page="true"): 
        uuid_query = "SELECT * from " + self.table_id1
        if page == "rue":
            uuid_query += " Limit " + str(50)
        print (uuid_query)
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()  # Wait for the job to complete. 
        return results

    def get_contracts_id(self, id): 
        uuid_query = "SELECT * from " + self.table_id1 + " where id = \'" + id + "\'"
        print (uuid_query)
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()  # Wait for the job to complete. 
        return results

    def update_contracts_id(self, id, title, content, response): 
        uuid_query = "UPDATE " + self.table_id1 + " SET response = \'" + response + \
            "\', title = \'" + title + "\', content = \'" + content + "\' where id = \'" + id + "\'"
        print (uuid_query)
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()
        return results

    def delete_contracts_id(self, id): 
        uuid_query = "Delete from " + self.table_id1 + " where id = \'" + id + "\'"
        print (uuid_query)
        query_job = self.client.create_job(
            job_config={
                "query": {
                    "query": uuid_query
                }
            }
        )  # Make an API request.

        print(f"Started job: {query_job.job_id}")
        return None
    
    def save_contracts(self, title, content, type = 'curated', response = '', domain = 'liability', userid='admin'): 
        uu_id = str(uuid.uuid4())

        rows_to_insert = [
            {"id": uu_id, "created" : "2022-01-01 01:01", "title" : title, "content" : content,  "type" : type, "response" : response, "domain" : domain, "userid" : userid}
            ]

        errors = self.client.insert_rows_json(
            self.table_id1, rows_to_insert, row_ids=[None] * len(rows_to_insert)
        )  # Make an API request.
        if errors == []:
            print("New rows have been added.", self.table_id1)
        else:
            print("Encountered errors while inserting rows: {}".format(errors))
        return uuid

    def save_contracts_batch(self, batch_data):
        rows_to_insert = []
        for row in batch_data:
            uu_id = str(uuid.uuid4())    
            insert_stmt =  {"id": uu_id, "created" : "2022-01-01 01:01", "title" : row['title'], "content" : row['content'],  "type" : "curated", "response" : row['response'], "domain" : "liability", "userid" : "admin"}               
            rows_to_insert.append(insert_stmt)
        #print (rows_to_insert)
        errors = self.client.insert_rows_json(
            self.table_id1, rows_to_insert, row_ids=[None] * len(rows_to_insert)
        )  # Make an API request.
        if errors == []:
            print("New rows have been added.", self.table_id2)
        else:
            print("Encountered errors while inserting rows: {}".format(errors))
        
        return None

    # Learn DB CRUD 
    def get_seed_data(self): 
        uuid_query = "SELECT * from " + self.table_id2
        print (uuid_query)
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()  # Wait for the job to complete. 
        return results

    def get_seed_data_id(self, id): 
        uuid_query = "SELECT * from " + self.table_id2 + " where id = \'" + id + "\'"
        print (uuid_query)
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()  # Wait for the job to complete. 
        return results

    def save_seed_data(self, keywords, content, label, type='curated', domain = 'liability', userid='admin'):
        uu_id = str(uuid.uuid4())

        rows_to_insert = [
            {"id": uu_id, "created" : "2022-01-01 01:01", "keywords" : keywords, "content" : content, "label" : label, "type" : type, "domain" : domain, "userid" : userid}
            ]

        errors = self.client.insert_rows_json(
            self.table_id2, rows_to_insert, row_ids=[None] * len(rows_to_insert)
        )  # Make an API request.
        if errors == []:
            print("New rows have been added.", self.table_id2)
        else:
            print("Encountered errors while inserting rows: {}".format(errors))
        
        return uuid

    def save_seed_data_batch(self, batch_data):
        rows_to_insert = []
        for row in batch_data:
            uu_id = str(uuid.uuid4())           
            insert_stmt = {"id": uu_id, "created" : "2022-01-01 01:01", "keywords" : row['keywords'], "content" : row['content'], "label" : row['label'], "type" : row['type'], "domain" : row['domain'], "userid" : row['userid']}
               
            rows_to_insert.append(insert_stmt)
        print (rows_to_insert)
        errors = self.client.insert_rows_json(
            self.table_id2, rows_to_insert, row_ids=[None] * len(rows_to_insert)
        )  # Make an API request.
        if errors == []:
            print("New rows have been added.", self.table_id2)
        else:
            print("Encountered errors while inserting rows: {}".format(errors))
        
        return uuid

    def update_seed_data_id(self, id, keywords): 
        uuid_query = "UPDATE " + self.table_id2 + " SET keywords = \'" + keywords + \
            "\' where id = \'" + id + "\'"
        print (uuid_query)
        query_job = self.client.create_job(
            job_config={
                "query": {
                    "query": uuid_query
                }
            }
        )  # Make an API request.

        print(f"Started job: {query_job.job_id}")
        return None 

    def update_seed_data_batch(self, batch_update): 
        uuid_query = ""
        for results in batch_update:
            uuid_query += "UPDATE " + self.table_id2 + " SET keywords = \"" + results['keywords']  + "\" where id = \"" + results['id'] + "\";\n"
        print (uuid_query)
        query_job = self.client.create_job(
            job_config={
                "query": {
                    "query": uuid_query
                }
            }
        )  # Make an API request.

        print(f"Started job: {query_job.job_id}")
        return 

    def delete_seed_data_id(self, id): 
        uuid_query = "Delete from " + self.table_id2 + " where id = \'" + id + "\'"
        print (uuid_query)
        query_job = self.client.create_job(
            job_config={
                "query": {
                    "query": uuid_query
                }
            }
        )  # Make an API request.

        print(f"Started job: {query_job.job_id}")
        return None 

    # Training Data CRUD 
    def save_training_data(self, content, type, label='', eval_label='', score=0, eval_score=0, domain = 'liability'): 
        uu_id = str(uuid.uuid4())

        rows_to_insert = [
            {"id": uu_id, "created" : "2022-01-01 01:01", "content" : content, "type" : type, "label" : label, "eval_label" : eval_label, "score" : int(score), "eval_score" : int(eval_score), "domain" : domain}
            ]

        errors = self.client.insert_rows_json(
            self.table_id3, rows_to_insert, row_ids=[None] * len(rows_to_insert)
        )  
        if errors == []:
            print("New rows have been added.", self.table_id3)
        else:
            print("Encountered errors while inserting rows: {}".format(errors))
        return uuid

    def save_training_data_batch(self, batch_data): 
        rows_to_insert = []
        for row in batch_data:
            uu_id = str(uuid.uuid4())           
            insert_stmt = {"id": uu_id, "created" : "2022-01-01 01:01", "content" : row['content'], "type" : row['type'], "label" : row['label'], "eval_label" : row['eval_label'], "score" : int(row['score']), "eval_score" : int(row['eval_score']), "domain" : row['domain']}
            
            rows_to_insert.append(insert_stmt)
        print (rows_to_insert)
        errors = self.client.insert_rows_json(
            self.table_id3, rows_to_insert, row_ids=[None] * len(rows_to_insert)
        )  # Make an API request.
        if errors == []:
            print("New rows have been added.", self.table_id3)
        else:
            print("Encountered errors while inserting rows: {}".format(errors))
        
        return None

    def get_training_data(self, type="all"): 
        uuid_query = "SELECT * from " + self.table_id3 
        if not type == "all":
            uuid_query = "SELECT * from " + self.table_id3 + " where type=\'" + type + "\'"
        print(uuid_query)
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()  # Wait for the job to complete. 
        return results

    def update_training_data(self, id, eval_label, eval_score): 
        uuid_query = "UPDATE " + self.table_id3 + " SET eval_label = \"" + eval_label  + \
            "\", eval_score = " + str(int(eval_score)) + " where id = \"" + id + "\""
        print (uuid_query)
        query_job = self.client.create_job(
            job_config={
                "query": {
                    "query": uuid_query
                }
            }
        )  # Make an API request.

        print(f"Started job: {query_job.job_id}")
        return 
    
    def update_training_data_batch(self, batch_update): 
        uuid_query = ""
        for results in batch_update:
            uuid_query += "UPDATE " + self.table_id3 + " SET eval_label = \"" + results['eval_label']  + \
                "\", eval_score = " + str(int(results['eval_score'])) + " where id = \"" + results['id'] + "\";\n"
        print (uuid_query)
        query_job = self.client.create_job(
            job_config={
                "query": {
                    "query": uuid_query
                }
            }
        )  # Make an API request.

        print(f"Started job: {query_job.job_id}")
        return 

    def training_data_cleanup(self, type):
        delete_sql = "Delete from " + self.table_id3 + " where type=\'" + type + "\'"
        print (delete_sql)
        query_job = self.client.create_job(
            job_config={
                "query": {
                    "query": delete_sql
                }
            }
        )  # Make an API request.

        print(f"Started job: {query_job.job_id}")
        return
