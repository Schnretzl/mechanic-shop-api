import os
from dotenv import load_dotenv

load_dotenv()

class DevelopmentConfig:
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://root:{MYSQL_PASSWORD}@localhost/mechanic_shop'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    
class TestingConfig:
    pass

class ProductionConfig:
    pass