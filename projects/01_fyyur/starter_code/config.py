import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
DB_USER = os.getenv('DB_USER', default='postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', default='password')
DB_NAME = os.getenv('DB_NAME', default='fyyur')
DB_DOMAIN = os.getenv('DB_DOMAIN', default='localhost')
DB_PORT = os.getenv('DB_PORT', default='5432')
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_DOMAIN}:{DB_PORT}/{DB_NAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
