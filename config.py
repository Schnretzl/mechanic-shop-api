import os

class DevelopmentConfig:
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://root:{MYSQL_PASSWORD}@localhost/mechanic_shop'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    
class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'

class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    CACHE_TYPE = 'SimpleCache'