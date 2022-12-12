import os

class Config(object):
    TESTING = True

class ProductionConfig(Config):
    FLASK_APP='src/app'
    FLASK_ENV='production'
    DOMAINS =['liabilities', 'esg']
    DEFAULT_DOMAIN = 'esg'
    DB_HOST = '34.93.121.15'
    DB_USER = 'root'
    DB_PASSWORD = 'Nu123456$$'
    DB_NAME = 'lca_prod'
    DATA_ENV = 'local'
    STORAGE_BUCKET = 'lca_prod'
    APP_MODE= 'accuracy'

class DevelopmentConfig(Config):
    FLASK_APP='src/app'
    FLASK_ENV='development'   
    DOMAINS =['liabilities', 'esg']
    DEFAULT_DOMAIN = 'esg'
    DB_HOST = '34.93.121.15'
    DB_USER = 'root'
    DB_PASSWORD = 'Nu123456$$'
    DB_NAME = 'lca_dev'
    DATA_ENV = 'local' 
    STORAGE_BUCKET = 'lca_dev'
    APP_MODE= 'accuracy'

class TestingConfig(Config):
    DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True



