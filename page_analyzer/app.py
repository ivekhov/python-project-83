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
except Exception as e:
    logging.warning(f"Can`t establish connection to database: {e}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '')

        errors = validate(url)
        if errors:
            flash(errors, 'danger')
            return redirect(url_for('index'))

        try:
            with conn.cursor() as cursor:

                # ToDo: Add URL to the database only if it is not already there
                cursor.execute("SELECT name FROM urls WHERE name = %s", (url,))
                if cursor.fetchone():
                    flash(f'URL {url} already exists', 'danger')
                    return redirect(url_for('index'))
                


                cursor.execute("INSERT INTO urls (name) VALUES (%s)", (url,))
                conn.commit()
                flash(f'URL {url} successfully added', 'success')

                messages = get_flashed_messages(with_categories=True)
                return render_template(
                    'index.html',
                    messages=messages
                )

        except Exception as e:
            conn.rollback()
            logging.error(f"Error adding URL to database: {e}")
            flash('An error occurred while adding the URL', 'danger')
        return redirect(url_for('index'))
    return render_template('index.html')


# ToDo: Реализуйте вывод всех добавленных URL на отдельной странице /urls и проверьте, что новые записи отображаются первыми
@app.route('/urls')
def urls_get():
    messages = get_flashed_messages(with_categories=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM urls ORDER BY id DESC")
            urls = cursor.fetchall()

            # ToDo: convert list of tuples to list of strings
            urls = [url[0] for url in urls]

            messages = get_flashed_messages(with_categories=True)
            return render_template('urls/index.html', urls=urls, messages=messages)
    except Exception as e:
        logging.error(f"Error getting URLs from database: {e}")
        flash('An error occurred while getting URLs', 'danger')
        return redirect(url_for('index'))


# ToDo: Реализуйте вывод конкретного введенного URL на отдельной странице urls/<id>
@app.route('/urls/<int:id>')
def url_get(id):
    messages = get_flashed_messages(with_categories=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM urls WHERE id = %s", (id,))
            url = cursor.fetchone()
            if not url:
                flash(f'URL with id {id} not found', 'danger')
                return redirect(url_for('index'))
            url = url[0]

            messages = get_flashed_messages(with_categories=True)
            return render_template('urls/show.html', url=url, messages=messages)
    except Exception as e:
        logging.error(f"Error getting URL from database: {e}")
        flash('An error occurred while getting URL', 'danger')
        return redirect(url_for('index'))


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
