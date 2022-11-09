
import mysql.connector

from mysql.connector.constants import ClientFlag, 
import os
import datetime

config1 = {
    'user': 'root',
    'password': '7gDKj,>,*2A}7BXj',
    'host': '34.28.58.198',
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': './store/sqldb/server-ca.pem',
    'ssl_cert': './store/sqldb/client-cert.pem',
    'ssl_key': './store/sqldb/client-key.pem'
}

config2 = {
    'user': 'root',
    'password': '7gDKj,>,*2A}7BXj',
    'host': '34.28.58.198',
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': './store/sqldb/server-ca.pem',
    'ssl_cert': './store/sqldb/client-cert.pem',
    'ssl_key': './store/sqldb/client-key.pem',
    'database' : 'lca_db'
}

schema_contract_data = "CREATE TABLE IF NOT EXISTS contract_data (" + \
               "id VARCHAR(255) NOT NULL, " + \
               "created DATETIME, " + \
               "title VARCHAR(255), " + \
               "content LONGTEXT, " + \
               "response LONGTEXT, " + \
               "userid VARCHAR(255));"


schema_seed_data = "CREATE TABLE IF NOT EXISTS seed_data (" + \
               "id VARCHAR(255) NOT NULL, " + \
               "created DATETIME, " + \
               "keywords LONGTEXT, " + \
               "content LONGTEXT, " + \
               "label LONGTEXT);" 
 
schema_training_data = "CREATE TABLE IF NOT EXISTS training_data (" + \
               "id VARCHAR(255) NOT NULL, " + \
               "created DATETIME, " + \
               "content LONGTEXT, " + \
               "label LONGTEXT, " + \
               "type LONGTEXT, " + \
               "eval_label LONGTEXT);"
 
class SQLUtility:
    def __init__(self) -> None:
        pass

    def create_database(self):
        cnxn = mysql.connector.connect(**config1)
        cursor = cnxn.cursor()  

        try:
            cursor.execute('CREATE DATABASE lca_db')
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        else:
            print('Database lca_db successfully created.')

        try: 
            cursor.execute(schema_contract_data)  
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        else:
            print('Table contract_data successfully created.')

        try: 
            cursor.execute(schema_seed_data)  
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        else:
            print('Table seed_data successfully created.')
        
        try: 
            cursor.execute(schema_training_data)  
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        else:
            print('Table training_data successfully created.')
        
        cnxn.close()
        return            

    def db_cleanup(self):
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  
        try:
            cursor.execute('DROP table contract_data')
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        else:
            print('Table contract_data successfully deleted.')
        try:
            cursor.execute('DROP table seed_data')
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        else:
            print('Table seed_data successfully deleted.')
        try:
            cursor.execute('DROP table training_data')
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        else:
            print('Table training_data successfully deleted.')
        try:
            cursor.execute('DELETE DATABASE lca_db')
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        else:
            print('Database lca_db deleted.')
        
        cnxn.close()
        return 

    # Contracts CRUD 
    def get_contracts(self, page="true"): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  
        qeuryquery_str = "Select * from contract_data LIMIT = 50"
        cursor.execute(qeuryquery_str)
        results = cursor.fetchall()
        cnxn.close()
        return results

    def get_contracts_id(self, id): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  
        qeuryquery_str = "Select * from contract_data where id =%s"
        val = (id,)
        cursor.execute(qeuryquery_str, val)
        results = cursor.fetchall()
        cnxn.close()
        return results

    def save_contracts(self, title, content, response): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  
        uuid_query = "SELECT UUID() AS uuid;"
        cursor.execute(uuid_query)
        results = cursor.fetchall()
        uuid = ''
        if results:
            for row in results:
                uuid = row[0]

        insert_stmt = ("INSERT INTO contract_data (id, created, title, content, response, userid) " 
                "VALUES (%s, %s, %s, %s, %s, %s)")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        data = (uuid, timestamp, title, content, response, "admin")

        cursor.execute(insert_stmt, data)
        cnxn.commit()

        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return 

    def update_contracts_id(self, id, title, content, response): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  

        sql = "UPDATE contract_data SET title = %s, content = %s, response = %s WHERE id = %s"
        val = (title, content, response, id)

        cursor.execute(sql, val)
        cnxn.commit()
        print(cursor.rowcount, "record(s) affected")

        cnxn.close()
        return 

    def delete_contracts_id(self, id): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  
        sql = "DELETE from contract_data where id = %s;"
        val = (id, )
        cursor.execute(sql, val)
        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return 

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
        return 

    def delete_seed_data_id(self, id): 
        uuid_query = "Delete from " + self.table_id2 + " where id = \'" + id + "\'"
        print (uuid_query)
        query_job = self.client.query(uuid_query)  # Make an API request.
        #results = query_job.result()  # Wait for the job to complete. 
        return   

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
        return 

    def training_data_cleanup(self, type):
        delete_sql = "Delete from " + self.table_id3 + " where type=\'" + type + "\'"
        print (delete_sql)
        query_job = self.client.query(delete_sql)

