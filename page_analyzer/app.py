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
from werkzeug.exceptions import HTTPException

from page_analyzer.parser import parse_url
from page_analyzer.urls import (
    clear_url,
    validate_url
)
from page_analyzer.url_repository import UrlRepository


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

repo = UrlRepository(app.config['DATABASE_URL'])


@app.errorhandler(404)
def handle_http_exception(e):
    flash('Произошла ошибка при проверке', 'danger')
    return redirect(url_for('index'))


@app.errorhandler(500)
def handle_server_error(e):
    flash('Произошла ошибка при проверке', 'danger')
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index() -> Response:
    """Render the index page.

    Returns:
        Response: The rendered index page.
    """
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def get_urls() -> Union[Response, str]:
    """Handle URL submission and display the list of URLs.

    Returns:
        Union[Response, str]: The rendered template or a redirect response.
    """
    url = ''
    if request.method == 'POST':
        url_raw = request.form.get('url', '')
        url = clear_url(url_raw)
        errors = validate_url(url)
        if errors:
            flash(errors[0], 'danger')
            response = render_template(
                'index.html',
                url=url_raw
            )
            return response, 422
        result = repo.find_id(url)
        if result:
            flash('Страница уже существует', 'info')
            url_id = result.get('id')
            return redirect(url_for('get_url', id=url_id))
        repo.save_url(url)
        flash('Страница успешно добавлена', 'success')

        url_id = repo.find_id(url).get('id')
        if url_id is None:
            abort(404)
        return redirect(url_for('get_url', id=url_id))

    if request.method == 'GET':
        urls = repo.get_urls()
        if urls is None:
            abort(404)
        return render_template(
            'list.html',
            urls=urls,
        )


@app.route('/urls/<int:id>')
def get_url(id: int) -> Union[Response, str]:
    """Display details for a specific URL. """
    url = repo.find_url_details(id)
    if url is None:
        abort(404)
    urls_checks = repo.get_checks(id)
    if urls_checks is None:
        abort(404)
    return render_template(
        'show.html',
        url=url,
        urls_checks=urls_checks
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_post(id: int):
    """Perform a check on the specified URL."""
    req = repo.find_url(id)
    if req is None:
        abort(404)
    url = req.get('name')
    response = requests.get(url)
    if not response.ok:
        abort(404)
    
    response.raise_for_status()
    status_code = response.status_code

    content = response.content
    url_parsed = parse_url(
        content
    )
    url_parsed['url_id'] = id
    url_parsed['status_code'] = status_code

    repo.save_checks(url_parsed)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url', id=id))


if __name__ == "__main__":
    app.run()
