import logging
import os
from datetime import datetime
from typing import Union
from urllib.parse import urlparse

import psycopg2
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    Response,
    request,
    url_for,
    g
)
from psycopg2.extras import DictCursor
from validators.url import url as is_url


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def get_db_connection():
    if 'conn' not in g:
        try:
            g.conn = psycopg2.connect(DATABASE_URL)
            logging.info("Connection to database established")
        except Exception as e:
            logging.warning(f"Can't establish connection to database: {e}")
            g.conn = None
    return g.conn


@app.teardown_appcontext
def close_db_connection(exception):
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()
        logging.info("Database connection closed")


@app.route('/', methods=['GET', 'POST'])
def index() -> Response:
    """Render the index page.

    Returns:
        Response: The rendered index page.
    """
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls_get() -> Union[Response, str]:
    """Handle URL submission and display the list of URLs.

    Returns:
        Union[Response, str]: The rendered template or a redirect response.
    """
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
            response = render_template(
                'index.html',
                messages=messages,
                url=url_raw
            )
            return response, 422

        conn = get_db_connection()
        if conn is None:
            flash('An error occurred while connecting to the database', 'danger')
            return redirect(url_for('index'))

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM urls WHERE name = %s", (url,))
                result = cursor.fetchone()
                if result:
                    flash('Страница уже существует', 'info')
                    url_id = result[0]
                    return redirect(url_for('url_get', id=url_id))

                cursor.execute("INSERT INTO urls (name) VALUES (%s)", (url,))
                conn.commit()
                flash('Страница успешно добавлена', 'success')

                cursor.execute("SELECT id FROM urls WHERE name = %s", (url,))
                url_id = cursor.fetchone()[0]
                return redirect(url_for('url_get', id=url_id))

        except Exception as e:
            conn.rollback()
            logging.error(f"Error adding URL to database: {e}")
            flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('index'))

    if request.method == 'GET':
        messages = get_flashed_messages(with_categories=True)
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error', 'danger')
            return redirect(url_for('index'))

        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                sql = """
                    WITH cte AS (
                        SELECT
                            u.id as id,
                            u.name AS name,
                        TO_CHAR(MAX(ch.created_at), 'YYYY-MM-DD') as last_checked,
                        MAX(ch.id) as last_check_id
                        FROM urls AS u
                            LEFT JOIN url_checks AS ch ON ch.url_id = u.id
                        GROUP BY 1, 2
                        ORDER BY 1 DESC
                    ) SELECT
                        cte.id as id,
                        cte.name as name,
                        cte.last_checked as last_checked,
                        cheks.status_code as status_code
                    FROM cte LEFT JOIN url_checks as cheks ON cte.last_check_id = cheks.id;
                    """
                cursor.execute(sql)
                urls = cursor.fetchall()
                return render_template(
                    'list.html',
                    urls=urls,
                )
        except Exception as e:
            logging.error(f"Error getting URLs from database: {e}")
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('index'))


@app.route('/urls/<int:id>')
def url_get(id: int) -> Union[Response, str]:
    """Display details for a specific URL.

    Args:
        id (int): The ID of the URL.

    Returns:
        Union[Response, str]: The rendered template or a redirect response.
    """
    messages = get_flashed_messages(with_categories=True)
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'danger')
        return redirect(url_for('index'))

    try:
        with conn.cursor() as cursor:

            # info about url
            cursor.execute("SELECT id, name, created_at FROM urls WHERE id = %s", (id,))
            url = cursor.fetchone()
            url = {
                'id': url[0],
                'name': url[1],
                'created_at': datetime.strftime(url[2], '%Y-%m-%d')
            }
            logging.warning(f"url: {url}")

            sql = f"""
            SELECT id, TO_CHAR(created_at, 'YYYY-MM-DD') as created_at, status_code, h1, title, description
            FROM url_checks
            WHERE url_id = {id} AND status_code IS NOT NULL
            ORDER BY id DESC;
            """
            cursor.execute(sql)
            urls_raw = cursor.fetchall()

            urls_checks = []
            for check in urls_raw:
                urls_checks.append(
                    {
                        'id': check[0],
                        'created_at': check[1],
                        'status_code': check[2],
                        'h1': check[3],
                        'title': check[4],
                        'description': check[5]
                    }
                )
            logging.warning(f"urls_checks: {urls_checks}")

        return render_template(
            'show.html',
            url=url,
            messages=messages,
            urls_checks=urls_checks
        )
    except Exception as e:
        logging.error(f"Error getting URL from database: {e}")
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('index'))


def validate(url: str) -> list[str]:
    """Validate the given URL.

    Args:
        url (str): The URL to validate.

    Returns:
        list[str]: A list of validation error messages.
    """
    errors = []
    if not is_url(url):
        errors.append('Некорректный URL')
        return errors
    if len(url) > 255:
        errors.append('URL превышает 255 символов')
        return errors
    return errors


@app.route('/urls/<int:id>/checks', methods=['POST'])
def checks_post(id: int) -> Response:
    """Perform a check on the specified URL.

    Args:
        id (int): The ID of the URL to check.

    Returns:
        Response: A redirect response to the URL details page.
    """

    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'danger')
        return redirect(url_for('url_get', id=id))

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM urls WHERE id = %s", (id,))
            url = cursor.fetchone()[0]

            try:
                response = requests.get(url)
                response.raise_for_status()
                status_code = response.status_code

                soup = BeautifulSoup(response.content, 'html.parser')
                h1_tag = soup.find('h1')
                h1_text = h1_tag.get_text(strip=True) if h1_tag else None

                title_tag = soup.find('title')
                title_text = title_tag.get_text(strip=True) if title_tag else None

                meta_description_tag = soup.find('meta', attrs={'name': 'description'})
                meta_description_text = meta_description_tag.get('content').strip() if meta_description_tag else None

            except requests.exceptions.RequestException as e:
                logging.error(f"Error checking URL: {e}")
                flash('Произошла ошибка при проверке', 'danger')
                return redirect(url_for('url_get', id=id))

            cursor.execute(
                "INSERT INTO url_checks (url_id, status_code, h1, title, description) VALUES (%s, %s, %s, %s, %s)",
                (id, status_code, h1_text, title_text, meta_description_text)
            )
            conn.commit()
            flash('Страница успешно проверена', 'success')

            cursor.execute("SELECT id, TO_CHAR(created_at, 'YYYY-MM-DD') as created_at, status_code, h1, title, description FROM url_checks WHERE url_id = %s ORDER BY id desc", (id,))
            urls_raw = cursor.fetchall()

            urls_checks = []
            for url_check in urls_raw:
                urls_checks.append(
                    {
                        'id': url_check[0],
                        'created_at': url_check[1],
                        'status_code': url_check[2],
                        'h1': url_check[3],
                        'title': url_check[4],
                        'description': url_check[5]
                    }
                )

    except Exception as e:
        conn.rollback()
        logging.error(f"Error creating check: {e}")
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_get', id=id))

    return redirect(url_for('url_get', id=id))


if __name__ == "__main__":
    app.run()
