import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask import render_template
import psycopg2


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    logging.info("Connection to database established")
except:
    logging.error("Can`t establish connection to database")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def hello_world():
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
