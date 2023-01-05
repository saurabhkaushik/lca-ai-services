import sqlite3, logging

class DBUtility: 
    db_file_url = '/Users/saurabhkaushik/Workspace/lca-web-ui/database.db'

    def __init__(self) -> None:
        pass

    def get_db_connection(self):
        conn = sqlite3.connect(self.db_file_url)
        conn.row_factory = sqlite3.Row
        return conn
        
    def get_learndb(self):
        conn = self.get_db_connection()
        posts = conn.execute('SELECT * FROM learndb').fetchall()
        conn.close()
        return posts