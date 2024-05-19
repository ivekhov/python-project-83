import os

from dotenv import load_dotenv
from flask import Flask


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def hello_world():
    return 'Welcome to Page Analyzer!'


if __name__ == "__main__":
    app.run()
