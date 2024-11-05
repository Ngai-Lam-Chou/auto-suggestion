import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Base directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'trie_search.db'))
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    # CORS settings
    CORS_HEADERS = 'Content-Type'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Dictionary of configuration classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}