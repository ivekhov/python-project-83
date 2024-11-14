from datetime import datetime
import logging
import os
from urllib.parse import urlparse

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
from validators.url import url as is_url


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
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls_get():

    url = ''
    if request.method == 'POST':
        url_raw = request.form.get('url', '')
        logging.warning(f"URL: {url} received")
        parsed = urlparse(url_raw)
        url = f"{parsed.scheme}://{parsed.hostname}"

        errors = validate(url)

        if errors:
            flash(errors[0], 'danger')
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'index.html',
                messages=messages,
                url=url_raw
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
        return redirect(url_for('index'))


    if request.method == 'GET':
        messages = get_flashed_messages(with_categories=True)
        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM urls ORDER BY id DESC")
                urls = cursor.fetchall()
                return render_template(
                    'list.html',
                    urls=urls,
                    messages=messages
                )
        except Exception as e:
            logging.error(f"Error getting URLs from database: {e}")
            flash('An error occurred while getting URLs', 'danger')
            return redirect(url_for('index'))



@app.route('/urls/<int:id>')
def url_get(id):
    messages = get_flashed_messages(with_categories=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, created_at FROM urls WHERE id = %s", (id,))
            url = cursor.fetchone()
            if not url:
                flash(f'URL with id {id} not found', 'danger')
                return redirect(url_for('index'))
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
        return redirect(url_for('index'))


def validate(url):
    errors = []
    if not is_url(url):
        errors.append('Это не URL')
        return errors
    if len(url) > 255:
        errors.append('URL превышает 255 символов')
        return errors
    return errors
    # example of error url:
    # https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.jsha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p/bootstrap.bundle.min.jsha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1bootstrap.bundle.min.jsha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1


if __name__ == "__main__":
    app.run()
