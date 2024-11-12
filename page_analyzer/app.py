import logging
import os

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
    session
)
import psycopg2


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    logging.info("Connection to database established")
except:
    logging.warning("Can`t establish connection to database")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


# ToDo: 
# Реализуйте форму ввода адреса на главной странице и обработчик, который добавляет введенную информацию в базу данных
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        url = request.form['url']
        print(url)
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO urls (name) VALUES (%s)", (url,))
                conn.commit()
                flash('URL successfully added', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('index'))
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
