import os

class Config(object):
    TESTING = True

class ProductionConfig(Config):
    FLASK_APP='src/app'
    FLASK_ENV='production'
    DOMAINS =['liabilities', 'esg']
    DEFAULT_DOMAIN = 'esg'
    DB_HOST = '34.170.168.203'
    DB_USER = 'root'
    DB_PASSWORD = 'nu123456'
    DB_NAME = 'lca_db'
    DATA_ENV = 'cloud'

class DevelopmentConfig(Config):
    FLASK_APP='src/app'
    FLASK_ENV='development'   
    DOMAINS =['liabilities', 'esg']
    DEFAULT_DOMAIN = 'esg'
    DB_HOST = '34.170.168.203'
    DB_USER = 'root'
    DB_PASSWORD = 'nu123456'
    DB_NAME = 'lca_db'
    DATA_ENV = 'local' 

class TestingConfig(Config):
    DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True



