import os
import secrets
from dotenv import load_dotenv


load_dotenv()


class CONFIG:
    SECRET_KEY = secrets.token_urlsafe(32)
    HOST = os.getenv('HOST')
    PORT = int(os.getenv('PORT'))
    BASE_URL=os.getenv('BASE_URL')

    KC_SERVER_URL = os.getenv("KC_SERVER_URL")
    KC_REALM = os.getenv("KC_REALM")
    KC_CLIENT_ID = os.getenv("KC_CLIENT_ID")
    KC_REDIRECT_URI = os.getenv("KC_REDIRECT_URI")
    

class DevelopmentConfig(CONFIG):
    DEBUG = True
    TESTING = True


class StagingConfig(CONFIG):
    DEBUG = False
    TESTING = False


class ProductionConfig(CONFIG):
    DEBUG = False
    TESTING = False


ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == 'development':
    APP_CONFIG = DevelopmentConfig
elif ENVIRONMENT == 'production':
    APP_CONFIG = ProductionConfig
elif ENVIRONMENT == 'staging':
    APP_CONFIG = StagingConfig