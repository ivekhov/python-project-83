install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

stop:
	lsof -ti :$(PORT) | xargs kill -9

test:
	poetry run pytest -vv

test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml

test-coverage-miss:
	poetry run pytest --cov-report term-missing --cov=page_analyzer

lint:
	poetry run flake8 page_analyzer

selfcheck:
	poetry check

check:
	selfcheck test lint

build:
	./build.sh
