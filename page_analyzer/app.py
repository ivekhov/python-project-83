import os
from typing import Union

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from requests import HTTPError

from page_analyzer.parser import parse_url
from page_analyzer.url_repository import UrlRepository
from page_analyzer.urls import clear_url, validate_url

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

repo = UrlRepository(app.config['DATABASE_URL'])


@app.errorhandler(404)
def handle_http_exception(e):
    flash('Произошла ошибка при проверке', 'danger')
    return redirect(url_for('get_index'))


@app.errorhandler(500)
def handle_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def get_index() -> Response:
    """Render the index page.

    Returns:
        Response: The rendered index page.
    """
    return render_template('index.html')


@app.route('/urls')
def get_urls() -> Union[Response, str]:
    """Handle URL submission and display the list of URLs.

    Returns:
        Union[Response, str]: The rendered template or a redirect response.
    """
    urls = repo.get_urls()
    return render_template(
        'list.html',
        urls=urls,
    )


@app.route('/urls', methods=['POST'])
def post_urls() -> Union[Response, str]:
    """Handle URL submission and display the list of URLs.

    Returns:
        Union[Response, str]: The rendered template or a redirect response.
    """
    url = ''
    url_raw = request.form.get('url', '')
    url = clear_url(url_raw)
    errors = validate_url(url)
    if errors:
        for error in errors:
            flash(error, 'danger')
        response = render_template(
            'index.html',
            url=url_raw
        )
        return response, 422
    url_id = repo.find_id(url)

    if url_id:
        flash('Страница уже существует', 'info')
        url_id = url_id.get('id')
        return redirect(url_for('get_url', url_id=url_id))
    url_id = repo.save_url(url)
    flash('Страница успешно добавлена', 'success')

    return redirect(
        url_for(
            'get_url',
            url_id=url_id
        )
    )


@app.route('/urls/<int:url_id>')
def get_url(url_id: int) -> Union[Response, str]:
    """Display details for a specific URL. """
    url = repo.find_url_details(url_id)
    urls_checks = repo.get_checks(url_id)
    return render_template(
        'show.html',
        url=url,
        urls_checks=urls_checks
    )


@app.route('/urls/<int:url_id>/checks', methods=['POST'])
def check_post(url_id: int):
    """Perform a check on the specified URL."""
    req = repo.find_url(url_id)
    if req is None:
        abort(404)
    url = req.get('name')
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        if not response.ok:
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('get_url', url_id=url_id))
        status_code = response.status_code
        content = response.content
        url_parsed = parse_url(content)
        url_parsed['url_id'] = url_id
        url_parsed['status_code'] = status_code

        repo.save_checks(url_parsed)
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('get_url', url_id=url_id))
    except HTTPError:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url', url_id=url_id))


if __name__ == "__main__":
    app.run()
