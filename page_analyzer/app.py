import os

from dotenv import load_dotenv
from flask import Flask
from flask import render_template


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def hello_world():
    return render_template('index.html')


# @app.route('/urls')
# def hello_world():
    # return render_template('index.html')
    # pass




if __name__ == "__main__":
    app.run()
