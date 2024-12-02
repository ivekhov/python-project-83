import logging
import os
from datetime import datetime
from typing import Union
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import (
    flash,
    Flask,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    Response,
    url_for
)
from validators.url import url as is_url

from page_analyzer.url_repository import UrlRepository


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

repo = UrlRepository(app.config['DATABASE_URL'])


@app.teardown_appcontext
def close_db_connection(exception):
    UrlRepository.close_db_connection(exception)


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

        conn = repo.get_connection()
        if conn is None:
            flash('An error occurred when connecting to the database', 'danger')
            return redirect(url_for('index'))

        try:
            result = repo.find_id(url)
            if result:
                flash('Страница уже существует', 'info')
                url_id = result[0]
                return redirect(url_for('url_get', id=url_id))

            repo.save_url(url)
            flash('Страница успешно добавлена', 'success')

            url_id = repo.find_id(url)[0]
            return redirect(url_for('url_get', id=url_id))

        except Exception as e:
            conn.rollback()
            logging.error(f"Error adding URL to database: {e}")
            flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('index'))

    if request.method == 'GET':
        messages = get_flashed_messages(with_categories=True)
        conn = repo.get_connection()
        if conn is None:
            flash('Database connection error', 'danger')
            return redirect(url_for('index'))

        try:
            urls = repo.get_content()
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
    conn = repo.get_connection()

    if conn is None:
        flash('Database connection error', 'danger')
        return redirect(url_for('index'))

    try:
        url = repo.find_url_details(id)

        url = {
            'id': url[0],
            'name': url[1],
            'created_at': datetime.strftime(url[2], '%Y-%m-%d')
        }
        logging.warning(f"url: {url}")
        urls_raw = repo.get_checks(id)

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
    conn = repo.get_connection()
    if conn is None:
        flash('Database connection error', 'danger')
        return redirect(url_for('url_get', id=id))

    try:
        req = repo.find_url(id)
        url = req[0]

        try:
            response = requests.get(url)
            response.raise_for_status()
            status_code = response.status_code

            soup = BeautifulSoup(response.content, 'html.parser')
            h1_tag = soup.find('h1')
            h1_text = h1_tag.get_text(strip=True) if h1_tag else None

            title_tag = soup.find('title')
            title_text = title_tag.get_text(strip=True) if title_tag else None

            meta_description_tag = soup.find(
                'meta',
                attrs={'name': 'description'}
            )
            meta_description_text = meta_description_tag \
                .get('content') \
                .strip() if meta_description_tag else None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error checking URL: {e}")
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('url_get', id=id))

        repo.save_checks(
            {
                'url_id': id,
                'status_code': status_code,
                'h1': h1_text,
                'title': title_text,
                'description': meta_description_text
            }
        )
        flash('Страница успешно проверена', 'success')

        urls_raw = repo.get_checks(id)
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
