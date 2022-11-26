import os

class Config(object):
    TESTING = True

class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'

class DevelopmentConfig(Config):
    FLASK_APP='src/app'
    FLASK_ENV='development'
    DOMAINS =['liabilities', 'esg']
    DEFAULT_DOMAINS = 'esg'
    GOOGLE_CERT_KEY = './store/genuine-wording-key.json'
    DB_HOST = '34.170.168.203'
    DB_USER = 'root'
    DB_PASSWORD = 'nu123456'
    APP_ENV = 'LOCAL' # 'LOCAL', 'CLOUD'

class TestingConfig(Config):
    DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
