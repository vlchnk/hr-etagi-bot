import psycopg2
import os
from urllib.parse import urlparse

# Bot using HR @hr_bot
bot = {'token': os.environ.get('BOT_TOKEN'), 'name': 'HREtagiBot', 'description': 'Bot for HR', 'url': os.environ.get('WEBHOOK_BOT')}

# Data for req to RIES
ries = {'login': os.environ.get('RIES_LOGIN'), 'password': os.environ.get('RIES_PASSWORD'), 'token': os.environ.get('RIES_TOKEN'), 'api_key': os.environ.get('API_KEY')}

# DB for bot hr_bot
db = os.environ.get('DATABASE_URL')

result = urlparse(db)
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port

# Connect db
conn = psycopg2.connect(
    database=database,
    user=username,
    password=password,
    host=hostname,
    port=port
)