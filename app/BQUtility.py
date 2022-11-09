from google.cloud import bigquery
from google.cloud.exceptions import NotFound, Conflict
import os

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
            bigquery.SchemaField("response", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("userid", "STRING", mode="NULLABLE")
        ]

        schema_seed_data = [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("keywords", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("content", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("label", "STRING", mode="NULLABLE")
        ]

        schema_training_data = [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("content", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("label", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("eval_label", "STRING", mode="NULLABLE")
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
        #self.client.delete_table(self.table_id1, not_found_ok=True)
        self.client.delete_table(self.table_id2, not_found_ok=True)
        self.client.delete_table(self.table_id3, not_found_ok=True)
        #self.client.delete_dataset(self.dataset_id, delete_contents=True, not_found_ok=True)
        print("Deleted dataset '{}'.".format(self.dataset_id))

    # Contracts CRUD 
    def get_contracts(self, page="true"): 
        uuid_query = "SELECT * from " + self.table_id1
        if page == "true":
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
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()
        return results
    
    def save_contracts(self, title, content, response): 
        uuid_query = "SELECT GENERATE_UUID() AS uuid;"
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()  # Wait for the job to complete. 
        for row in results:
            uuid = row.uuid

        rows_to_insert = [
            {"id": uuid, "title" : title, "content" : content, "created" : "2022-01-01 01:01", "response" : response, "userid" : "admin"}
            ]

        errors = self.client.insert_rows_json(
            self.table_id1, rows_to_insert, row_ids=[None] * len(rows_to_insert)
        )  # Make an API request.
        if errors == []:
            print("New rows have been added.")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))
        return uuid

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

    def save_seed_data(self, keywords, content, label):
        uuid_query = "SELECT GENERATE_UUID() AS uuid;"
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()  # Wait for the job to complete. 
        for row in results:
            uuid = row.uuid

        rows_to_insert = [
            {"id": uuid, "keywords" : keywords, "content" : content, "created" : "2022-01-01 01:01", "label" : label}
            ]

        errors = self.client.insert_rows_json(
            self.table_id2, rows_to_insert, row_ids=[None] * len(rows_to_insert)
        )  # Make an API request.
        if errors == []:
            print("New rows have been added.")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))
        
        return uuid

    def update_seed_data_id(self, id, keywords, content, label): 
        uuid_query = "UPDATE " + self.table_id2 + " SET keywords = \'" + keywords + \
            "\', content = \'" + content + "\', label = \'" + label + "\' where id = \'" + id + "\'"
        print (uuid_query)
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()
        return results

    def delete_seed_data_id(self, id): 
        uuid_query = "Delete from " + self.table_id2 + " where id = \'" + id + "\'"
        print (uuid_query)
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()
        #results = query_job.result()  # Wait for the job to complete. 
        return results 

    # Training Data CRUD 
    def save_training_data(self, content, label, type, eval_label): 
        uuid_query = "SELECT GENERATE_UUID() AS uuid;"
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()  # Wait for the job to complete. 
        for row in results:
            uuid = row.uuid

        rows_to_insert = [
            {"id": uuid, "content" : content, "created" : "2022-01-01 01:01", "label" : label, "type" : type, "eval_label" : eval_label}
            ]

        errors = self.client.insert_rows_json(
            self.table_id3, rows_to_insert, row_ids=[None] * len(rows_to_insert)
        )  
        if errors == []:
            print("New rows have been added.")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))
        return uuid

    def get_training_data(self, type="all"): 
        uuid_query = "SELECT * from " + self.table_id3 
        if not type == "all":
            uuid_query = "SELECT * from " + self.table_id3 + " where type=\'" + type + "\'"
        print(uuid_query)
        query_job = self.client.query(uuid_query)  # Make an API request.
        results = query_job.result()  # Wait for the job to complete. 
        return results

    def update_training_data(self, id, eval_label): 
        uuid_query = "UPDATE " + self.table_id3 + " SET eval_label = \'" + eval_label + "\'" + " where id = \'" + id + "\'"
        print (uuid_query)
        query_job = self.client.query(uuid_query)  # Make an API request.
        query_job.result()
        return 

    def training_data_cleanup(self, type):
        delete_sql = "Delete from " + self.table_id3 + " where type=\'" + type + "\'"
        print (delete_sql)
        query_job = self.client.query(delete_sql)
        query_job.result()
        return

