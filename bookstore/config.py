import os
import datetime
import ssl
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

    PROJECT_NAME_LOWER = 'bookstore'
    PROJECT_NAME_UPPER = 'BookStore'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kho doan vl luon'

    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    
    DB_HOST = os.environ.get('DB_HOST')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    BOTO3_ACCESS_KEY = AWS_ACCESS_KEY_ID
    BOTO3_SECRET_KEY = AWS_SECRET_ACCESS_KEY
    BOTO3_REGION = 'ap-southeast-1'
    BOTO3_SERVICES = ['s3']

    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    JWT_SECRET_KEY = os.environ.get('SECRET')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    # DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://%s:%s@%s/bookstore_dev' % (Config.DB_USERNAME, Config.DB_PASSWORD, Config.DB_HOST)


class TestingConfig(Config):
    TESTING = True  
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://%s:%s@%s/bookstore_test' % (Config.DB_USERNAME, Config.DB_PASSWORD, Config.DB_HOST)
    

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://%s:%s@%s/bookstore_pro' % (Config.DB_USERNAME, Config.DB_PASSWORD, Config.DB_HOST)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
