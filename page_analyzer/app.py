import logging
import os
from typing import Union

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.url_parser import (
    clear_url,
    parse,
    validate,
)
from page_analyzer.url_repository import UrlRepository

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


repo = UrlRepository(app.config['DATABASE_URL'])


@app.teardown_appcontext
def close_db_connection(exception):
    repo.close_connection(exception)


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
        url = clear_url(url_raw)
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

        try:
            result = repo.find_id(url)
            if result:
                flash('Страница уже существует', 'info')
                url_id = result.get('id')
                return redirect(url_for('url_get', id=url_id))
            repo.save_url(url)
            flash('Страница успешно добавлена', 'success')

            url_id = repo.find_id(url).get('id')
            return redirect(url_for('url_get', id=url_id))

        except Exception as e:
            logging.error(f"Error adding URL to database: {e}")
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('index'))

    if request.method == 'GET':
        messages = get_flashed_messages(with_categories=True)
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
    try:
        url = repo.find_url_details(id)
        urls_checks = repo.get_checks(id)
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


@app.route('/urls/<int:id>/checks', methods=['POST'])
def checks_post(id: int) -> Response:
    """Perform a check on the specified URL.

    Args:
        id (int): The ID of the URL to check.

    Returns:
        Response: A redirect response to the URL details page.
    """
    try:
        req = repo.find_url(id)
        url = req.get('name')
        response = requests.get(url)
        url_parsed = parse(response)
        url_parsed['url_id'] = id
        repo.save_checks(url_parsed)
        flash('Страница успешно проверена', 'success')
       
    except Exception as e:
        logging.error(f"Error checking URL: {e}")
        flash('Произошла ошибка при проверке', 'danger')

    finally:
        return redirect(url_for('url_get', id=id))


if __name__ == "__main__":
    app.run()
