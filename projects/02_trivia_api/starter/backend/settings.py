import os

DB_USER = os.environ.get('DB_USER', default='postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', default='password')
DB_DOMAIN = os.environ.get('DB_DOMAIN', default='localhost:5432')
DB_NAME = os.environ.get('DB_NAME', default='trivia')