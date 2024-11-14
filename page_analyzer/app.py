from datetime import datetime
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
from psycopg2.extras import DictCursor


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    logging.info("Connection to database established")
except Exception as e:
    logging.warning(f"Can`t establish connection to database: {e}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls_get():

    url = ''
    if request.method == 'POST':
        url = request.form.get('url', '')
        logging.warning(f"URL: {url} received")
        errors = validate(url)

        if errors:
            flash('URL превышает 255 символов', 'danger')
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'main.html',
                messages=messages,
                url=url
            )

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM urls WHERE name = %s", (url,))
                result = cursor.fetchone()
                if result:
                    flash('Страница уже существует', 'info')
                    id = result[0]
                    return redirect(url_for('url_get', id=id))

                cursor.execute("INSERT INTO urls (name) VALUES (%s)", (url,))
                conn.commit()
                flash('Страница успешно добавлена', 'success')

                cursor.execute("SELECT id FROM urls WHERE name = %s", (url,))
                id = cursor.fetchone()[0]
                return redirect(url_for('url_get', id=id))

        except Exception as e:
            conn.rollback()
        return redirect(url_for('main'))


    if request.method == 'GET':
        messages = get_flashed_messages(with_categories=True)
        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM urls ORDER BY id DESC")
                urls = cursor.fetchall()
                return render_template(
                    'index.html',
                    urls=urls,
                    messages=messages
                )
        except Exception as e:
            logging.error(f"Error getting URLs from database: {e}")
            flash('An error occurred while getting URLs', 'danger')
            return redirect(url_for('main'))



@app.route('/urls/<int:id>')
def url_get(id):
    messages = get_flashed_messages(with_categories=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, created_at FROM urls WHERE id = %s", (id,))
            url = cursor.fetchone()
            if not url:
                flash(f'URL with id {id} not found', 'danger')
                return redirect(url_for('main'))
            url = {'id': url[0], 'name': url[1], 'created_at': datetime.strftime(url[2], '%Y-%m-%d')}

            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'show.html',
                url=url,
                messages=messages
            )
    except Exception as e:
        logging.error(f"Error getting URL from database: {e}")
        flash('An error occurred while getting URL', 'danger')
        return redirect(url_for('main'))


def validate(url):
    errors = []
    if not url:
        errors.append('URL is required')
    if len(url) > 255:
        errors.append('URL must be less than 255 characters')
    return errors
    # example of error url:
    # https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.jsha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p/bootstrap.bundle.min.jsha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1bootstrap.bundle.min.jsha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1


if __name__ == "__main__":
    app.run()
