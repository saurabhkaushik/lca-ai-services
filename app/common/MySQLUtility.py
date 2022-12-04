import uuid
from mysql.connector import pooling
import datetime

import mysql.connector
from mysql.connector.constants import ClientFlag

db_config = {
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': './store/sqldb/server-ca.pem',
    'ssl_cert': './store/sqldb/client-cert.pem',
    'ssl_key': './store/sqldb/client-key.pem',
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


class MySQLUtility(object):
    connection_pool = None

    def __init__(self, db_host, db_user, db_password, db_name):
        if db_user != '':
            db_config['user'] = db_user
            db_config['password'] = db_password
            db_config['host'] = db_host
            db_config['database'] = db_name
        pass

    table_id1 = 'contract_data'
    table_id2 = 'seed_data'
    table_id3 = 'training_data'

    def get_connection(self):
        self.connect = self.connection_pool
        if self.connect == None:             
            try:
                self.connect = pooling.MySQLConnectionPool(pool_name="lca_ui_pool",
                                                            pool_size=5,
                                                            pool_reset_session=True,
                                                            **db_config)
            except mysql.connector.Error as err:
                print('DB Connection Error: ', err)
            finally:
                print("DB Pool Created.")
            self.connection_pool = self.connect

        connection = self.connect.get_connection()   

        if not connection.is_connected(): 
            print('DB Connection Error: ')
            self.connect = None 
            return None 
            
        return connection
        

    def create_database(self):
        cnxn = self.get_connection()
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
        cnxn = self.get_connection()
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
    def get_contracts(self, domain, page="true"):
        cnxn = self.get_connection()
        cursor = cnxn.cursor(dictionary=True)

        uuid_query = "Select * from contract_data" + " where domain=\'" + domain + '\';'
        cursor.execute(uuid_query)
        print(cursor.statement)

        results = cursor.fetchall()

        cnxn.close()
        return results

    def get_contracts_id(self, id):
        cnxn = self.get_connection()
        cursor = cnxn.cursor(dictionary=True)

        uuid_query = "Select * from contract_data where id =\"" + id + "\""
        cursor.execute(uuid_query)
        print(cursor.statement)

        results = cursor.fetchall()

        cnxn.close()
        return results

    def save_contracts_batch(self, batch_data):
        cnxn = self.get_connection()
        cursor = cnxn.cursor()
        uu_id = ''
        rows_to_insert = []
        insert_stmt = ("INSERT INTO contract_data (id, created, title, content, type, response, domain, userid) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        for row in batch_data:
            uu_id = str(uuid.uuid4())
            title = row['title']
            content = row['content']
            now = datetime.datetime.utcnow()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            insert_str = (uu_id, formatted_date, title, content,
                          row['type'], row['response'], row['domain'], row['userid'])
            rows_to_insert.append(insert_str)

        cursor.executemany(insert_stmt, rows_to_insert)
        print(cursor.statement)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return uu_id

    def update_contracts_id(self, id, title, content, response):
        cnxn = self.get_connection()
        cursor = cnxn.cursor()

        uuid_query = "UPDATE " + self.table_id1 + \
            " SET response = %s, title = %s, content = %s where id = %s;"
        val = (response, title, content, id)

        cursor.execute(uuid_query, val)
        print(cursor.statement)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return None

    def delete_contracts_id(self, id):
        cnxn = self.get_connection()
        cursor = cnxn.cursor()

        uuid_query = "Delete from " + self.table_id1 + " where id = \'" + id + "\'"
        cursor.execute(uuid_query)
        print(cursor.statement)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return None

    # Learn DB CRUD
    def get_seed_data(self, domain):
        cnxn = self.get_connection()
        cursor = cnxn.cursor(dictionary=True)

        uuid_query = "SELECT * from " + self.table_id2 + " where domain=\'" + domain + '\';'
        cursor.execute(uuid_query)
        results = cursor.fetchall()
        print(cursor.statement)

        cnxn.close()
        return results

    def get_seed_data_id(self, id):
        cnxn = self.get_connection()
        cursor = cnxn.cursor(dictionary=True)

        uuid_query = "SELECT * from " + self.table_id2 + " where id = \'" + id + "\'"
        cursor.execute(uuid_query)
        results = cursor.fetchall()
        print(cursor.statement)

        cnxn.close()
        return results

    def save_seed_data_batch(self, batch_data):
        cnxn = self.get_connection()
        cursor = cnxn.cursor()
        uu_id = ''
        rows_to_insert = []
        insert_stmt = ("INSERT INTO " + self.table_id2 + " (id, created, keywords, content, type, label, domain, userid) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);")
        for row in batch_data:
            uu_id = str(uuid.uuid4())
            now = datetime.datetime.utcnow()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            insert_set = (uu_id, formatted_date,
                          row['keywords'], row['content'], row['type'], row['label'], row['domain'], row['userid'])
            rows_to_insert.append(insert_set)

        cursor.executemany(insert_stmt, rows_to_insert)
        print(cursor.statement)

        cnxn.commit()
        cnxn.close()
        print('Query: ', cursor.rowcount, "record(s) affected")
        return uu_id

    def update_seed_data_id(self, id, keywords):
        cnxn = self.get_connection()
        cursor = cnxn.cursor()

        uuid_query = "UPDATE " + self.table_id2 + " SET keywords = %s where id = %s;"
        val = (keywords, id)
        cursor.execute(uuid_query, val)
        print(cursor.statement)

        cnxn.commit()
        cnxn.close()
        print('Query: ', cursor.rowcount, "record(s) affected")
        return None

    def update_seed_data_batch(self, batch_data):
        cnxn = self.get_connection()
        cursor = cnxn.cursor()

        rows_to_insert = []
        uuid_query = "UPDATE " + self.table_id2 + " SET keywords = %s where id = %s ; "

        for row in batch_data:
            insert_stmt = (row['keywords'], row['id'])
            rows_to_insert.append(insert_stmt)

        cursor.executemany(uuid_query, rows_to_insert)
        print(cursor.statement)

        cnxn.commit()
        cnxn.close()
        print('Query: ', cursor.rowcount, "record(s) affected")
        return None

    def delete_seed_data_id(self, id):
        cnxn = self.get_connection()
        cursor = cnxn.cursor()

        uuid_query = "Delete from " + self.table_id2 + " where id = \'" + id + "\'"
        cursor.execute(uuid_query)
        print(cursor.statement)

        cnxn.commit()
        cnxn.close()
        print('Query: ', cursor.rowcount, "record(s) affected")
        return None

    # Training Data CRUD
    def get_training_data(self, domain, type="all"):
        cnxn = self.get_connection()
        cursor = cnxn.cursor(dictionary=True)

        uuid_query = "SELECT * from " + self.table_id3 + " where domain=\'" + domain + '\';'
        if not type == "all":
            uuid_query = "SELECT * from " + self.table_id3 + " where type=\'" + type + "\'" + " and domain=\'" + domain + '\';'
        print('Query: ', uuid_query)
        cursor.execute(uuid_query)
        print(cursor.statement)

        results = cursor.fetchall()

        cnxn.close()
        return results

    def get_training_data_id(self, id):
        cnxn = self.get_connection()
        cursor = cnxn.cursor(dictionary=True)

        uuid_query = "SELECT * from " + self.table_id3 + " where id = \'" + id + "\'"
        cursor.execute(uuid_query)
        print(cursor.statement)

        results = cursor.fetchall()

        cnxn.close()
        return results

    def save_training_data_batch(self, batch_data):
        cnxn = self.get_connection()
        cursor = cnxn.cursor()

        rows_to_insert = []
        insert_stmt = ("INSERT INTO " + self.table_id3 + " (id, created, content, type, label, eval_label, score, eval_score, domain, userid) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        for row in batch_data:
            uu_id = str(uuid.uuid4())
            now = datetime.datetime.utcnow()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            insert_set = (uu_id, formatted_date, row['content'], row['type'], row['label'], row['eval_label'], int(
                row['score']), int(row['eval_score']), row['domain'], row['userid'])
            rows_to_insert.append(insert_set)

        cursor.executemany(insert_stmt, rows_to_insert)
        print(cursor.statement)

        cnxn.commit()
        cnxn.close()
        print('Query: ', cursor.rowcount, "record(s) affected")
        return None

    def update_training_data_batch(self, batch_data):
        cnxn = self.get_connection()
        cursor = cnxn.cursor()

        rows_to_insert = []

        uuid_query = "UPDATE " + self.table_id3 + \
            " SET score = %s, eval_label = %s, eval_score = %s where id = %s;"

        for row in batch_data:
            insert_stmt = (row['score'], row['eval_label'],
                           row['eval_score'], row['id'])
            rows_to_insert.append(insert_stmt)
        cursor.executemany(uuid_query, rows_to_insert)
        print(cursor.statement)

        cnxn.commit()
        cnxn.close()
        print(cursor.rowcount, "record(s) affected")
        return None

    def delete_training_data_id(self, id):
        cnxn = self.get_connection()
        cursor = cnxn.cursor()

        cnxn = mysql.connector.connect(**config2)
        cursor = cnxn.cursor()

        uuid_query = "Delete from " + self.table_id3 + " where id = \'" + id + "\'"
        cursor.execute(uuid_query)
        print(cursor.statement)

        cnxn.commit()
        cnxn.close()
        print('Query: ', cursor.rowcount, "record(s) affected")
        return None
