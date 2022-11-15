import datetime
import os
import uuid

import mysql.connector
from mysql.connector.constants import ClientFlag

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './store/genuine-wording-key.json'

config2 = {
    'user': 'root',
    'password': 'nu123456',
    'host': '34.170.168.203',
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
                "type VARCHAR(255), " + \
                "response LONGTEXT, " + \
                "domain VARCHAR(255), " + \
                "userid VARCHAR(255));"

schema_seed_data = "CREATE TABLE IF NOT EXISTS seed_data (" + \
                "id VARCHAR(255) NOT NULL, " + \
                "created DATETIME, " + \
                "keywords LONGTEXT, " + \
                "content LONGTEXT, " + \
                "type VARCHAR(255), " + \
                "label LONGTEXT, " + \
                "domain VARCHAR(255), " + \
                "userid VARCHAR(255));" 
 
schema_training_data = "CREATE TABLE IF NOT EXISTS training_data (" + \
                "id VARCHAR(255) NOT NULL, " + \
                "created DATETIME, " + \
                "content LONGTEXT, " + \
                "type VARCHAR(255), " + \
                "label VARCHAR(255), " + \
                "eval_label VARCHAR(255), " + \
                "score INTEGER, " + \
                "eval_score INTEGER, " + \
                "domain VARCHAR(255), " + \
                "userid VARCHAR(255));" 
 
class MySQLUtility:
    def __init__(self) -> None:
        pass

    table_id1 = 'contract_data'
    table_id2 = 'seed_data'
    table_id3 = 'training_data'

    def create_database(self):
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  
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

        cnxn.commit()
        cnxn.close()
        return            

    def clean_db(self):
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

        cnxn.commit()
        cnxn.close()
        return 

    # Contracts CRUD 
    def get_contracts(self, page="true"): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor(dictionary=True)  

        uuid_query = "Select * from contract_data"
        cursor.execute(uuid_query)
        results = cursor.fetchall()

        cnxn.close()
        return results

    def get_contracts_id(self, id): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor(dictionary=True)  

        uuid_query = "Select * from contract_data where id =\"" + id + "\""
        cursor.execute(uuid_query)
        results = cursor.fetchall()

        cnxn.close()
        return results

    def save_contracts_batch(self, batch_data):
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  
        uu_id = ''
        rows_to_insert = []
        insert_stmt = ("INSERT INTO contract_data (id, created, title, content, type, response, domain, userid) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        for row in batch_data:
            uu_id = str(uuid.uuid4())                
            insert_str =  (uu_id, "2022-01-01 01:01", row['title'], row['content'], row['type'], row['response'], row['domain'], row['userid'])               
            rows_to_insert.append(insert_str)
        
        cursor.executemany(insert_stmt, rows_to_insert)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return uu_id 
    
    def update_contracts_id(self, id, title, content, response): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor() 

        uuid_query = "UPDATE " + self.table_id1 + " SET response = \'" + response + \
            "\', title = \'" + title + "\', content = \'" + content + "\' where id = \'" + id + "\'"
        print (uuid_query)
        cursor.execute(uuid_query)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return None

    def delete_contracts_id(self, id): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor() 

        uuid_query = "Delete from " + self.table_id1 + " where id = \'" + id + "\'"
        print (uuid_query)
        cursor.execute(uuid_query)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return None

    # Learn DB CRUD 
    def get_seed_data(self): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor(dictionary=True)  

        uuid_query = "SELECT * from " + self.table_id2
        print (uuid_query)
        cursor.execute(uuid_query)
        results = cursor.fetchall()

        cnxn.close()
        return results

    def get_seed_data_id(self, id): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor(dictionary=True)  

        uuid_query = "SELECT * from " + self.table_id2 + " where id = \'" + id + "\'"
        print (uuid_query)
        cursor.execute(uuid_query)
        results = cursor.fetchall()

        cnxn.close()
        return results

    def save_seed_data_batch(self, batch_data):
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  
        uu_id = ''
        rows_to_insert = []
        insert_stmt = ("INSERT INTO " + self.table_id2 + " (id, created, keywords, content, type, label, domain, userid) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);")
        for row in batch_data:
            uu_id = str(uuid.uuid4())                
            insert_set =  (uu_id, "2022-01-01 01:01", row['keywords'], row['content'], row['type'], row['label'], row['domain'], row['userid'])
            rows_to_insert.append(insert_set)
        
        cursor.executemany(insert_stmt, rows_to_insert)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return uu_id 

    def update_seed_data_id(self, id, keywords): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  

        uuid_query = "UPDATE " + self.table_id2 + " SET keywords = \'" + keywords + \
            "\' where id = \'" + id + "\'"
        print (uuid_query)
        cursor.execute(uuid_query)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return None

    def update_seed_data_batch(self, batch_data): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  

        rows_to_insert = []
        uuid_query = "UPDATE " + self.table_id2 + " SET keywords = %s where id = %s ; "

        for row in batch_data:
            insert_stmt =  (row['keywords'], row['id'])               
            rows_to_insert.append(insert_stmt)

        print (rows_to_insert)
        cursor.executemany(uuid_query, rows_to_insert)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return None 

    def delete_seed_data_id(self, id): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  

        uuid_query = "Delete from " + self.table_id2 + " where id = \'" + id + "\'"
        print (uuid_query)
        cursor.execute(uuid_query)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return None

    # Training Data CRUD 
    def get_training_data(self, type="all"): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor(dictionary=True)  

        uuid_query = "SELECT * from " + self.table_id3 
        if not type == "all":
            uuid_query = "SELECT * from " + self.table_id3 + " where type=\'" + type + "\'"
        print(uuid_query)
        cursor.execute(uuid_query)
        results = cursor.fetchall()

        cnxn.close()
        return results
    
    def get_training_data_id(self, id): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor(dictionary=True)  

        uuid_query = "SELECT * from " + self.table_id3 + " where id = \'" + id + "\'"
        print (uuid_query)
        cursor.execute(uuid_query)
        results = cursor.fetchall()

        cnxn.close()
        return results

    def save_training_data_batch(self, batch_data): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  

        rows_to_insert = []
        insert_stmt = ("INSERT INTO " + self.table_id3 + " (id, created, content, type, label, eval_label, score, eval_score, domain, userid) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        for row in batch_data:
            uu_id = str(uuid.uuid4())                
            insert_set =  (uu_id, "2022-01-01 01:01", row['content'], row['type'], row['label'], row['eval_label'], int(row['score']), int(row['eval_score']), row['domain'], row['userid'])
            rows_to_insert.append(insert_set)
        
        cursor.executemany(insert_stmt, rows_to_insert)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return None 
    
    def update_training_data_batch(self, batch_data): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  

        rows_to_insert = []

        uuid_query = "UPDATE " + self.table_id3 + " SET score = %s, eval_label = %s, eval_score = %s where id = %s;"

        for row in batch_data:
            insert_stmt =  (row['score'], row['eval_label'], row['eval_score'], row['id'])               
            rows_to_insert.append(insert_stmt)
        cursor.executemany(uuid_query, rows_to_insert)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return None 

    def delete_training_data_id(self, id): 
        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  

        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()  

        uuid_query = "Delete from " + self.table_id3 + " where id = \'" + id + "\'"
        print (uuid_query)
        cursor.execute(uuid_query)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return None
