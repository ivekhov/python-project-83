# Project 3 "Page Analyzer"

**Part of Python Developer Profession on Hexlet**
https://hexlet.io/programs/python

**Official project description: demonstration**
https://python-page-analyzer-ru.hexlet.app/


## About tool

Page Analyzer

---



### Hexlet tests and linter status:
[![Actions Status](https://github.com/ivekhov/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/ivekhov/python-project-83/actions)


----
## How to


Install project: 
```bash
$ git clone https://github.com/ivekhov/python-project-83.git
$ make install
```

First time setup:

```bash:
$ export DATABASE_URL=postgresql://janedoe:mypassword@localhost:5432/mydb
$ chmod +x ./build.sh
```


Build project:

```bash
$ make build
```


Starting server locally:

```bash

# start server:
$ make start

# or:

# If port 8080 is in use, kill it:
$ lsof -ti :8080 | xargs kill -9

$ poetry run gunicorn -w 5 -b 0.0.0.0:8080 page_analyzer:app
```




Start server:
```bash
$ make start
```

## Public web-page:

https://python-project-83-rr2w.onrender.com/

----

### Задачи
https://ru.hexlet.io/projects/83/members/39478?step=3 


- [x] Создайте базы данных для разработки (локально на вашей машине) 

- [x] Создайте БД развернутого приложения (на сайте render)

- [x] Создайте в базе данных таблицу urls с полями id, name и created_at

- [x] В корне проекта создайте SQL-файл с таблицей и назовите его database.sql

- [x] Реализуйте форму ввода адреса на главной странице и обработчик, который добавляет введенную информацию в базу данных

- [x] Не забудьте, что имя поля ввода input должно быть url

- [x] Реализуйте валидацию для введенного URL-адреса. У URL обязательно должен быть валидный адрес, не превышающий 255 символов

- [x] Реализуйте вывод конкретного введенного URL на отдельной странице urls/<id>

- [x] Реализуйте вывод всех добавленных URL на отдельной странице /urls и проверьте, что новые записи отображаются первыми

- [x] Настройте рендеринг таблицы сайтов с помощью Bootstrap (см пример https://python-page-analyzer-ru.hexlet.app/urls )

- [x] Настройте рендеринг страницы отдельного сайта с помощью Bootstrap (https://python-page-analyzer-ru.hexlet.app/)

- [x] Настройте рендеринг flash-сообщений с помощью Bootstrap

- [x] Настройте рендеринг flash-сообщений об ошибках валидации на адресе /urls/ и сохранении адреса на главной странице

- [x] Задеплойте результат


### Требования
- [x] Используйте именованный роутинг
- [x] Помните, что имена сайтов должны быть уникальны. Добавление сайта с тем же именем не должно приводить к созданию новой записи в базе данных
- [x] Если данные не прошли валидацию, то должна рендериться форма с выводом ошибки
- [x] Используйте flash-сообщения для оповещения об успешном добавлении или ошибках
- [x] Используйте только стандартные возможности Bootstrap: Сетка, Компоненты, Утилиты
- [x] Проверьте, что значения атрибутов HTML-элементов форм, текст элементов Label форм, тексты кнопок и ссылок для перехода по страницам, flash-сообщения и другие тексты точно соответствуют демонстрационному проекту
- [x] У таблицы со списком адресов должен быть атрибут data-test="urls"
- [x] У таблицы с информацией об адресе должен быть атрибут data-test="url"
- [x] SQL-файл с созданными таблицами должен называться database.sql

## Postgres

```bash
# У строки следующий формат: {provider}://{user}:{password}@{host}:{port}/{db}

# example: 
# export DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/mydb

# start docker: from Docker Desktop: "postgres-container

# from termial:
docker exec -it postgres-container psql -U postgres -d hexlet
```


## Step 4

Задачи
- [x] Создайте таблицу url_checks с полями id, url_id, status_code, h1, title, description и created_at
- [x] Добавьте описание таблицы в файл database.sql
- [x] Реализуйте обработчик маршрута POST urls/<id>/checks и форму с кнопкой на странице сайта, при отправке которой происходит создание новой проверки. Обратите внимание, что на этом шаге заполняются только базовые поля (url_id и created_at)
- [x] Выведите идентификаторы и даты всех проверок на странице сайта
- [x] Выведите в списке сайтов дату последней проверки рядом с каждым сайтом
- [x] Задеплойте результат

## Step 5

Реализуйте настоящую проверку сайта на его доступность. Выполните запрос к нужному сайту и соберите информацию о нем.

Tasks: 

- [x] Во время проверки выполните запрос к сайту и извлеките код из ответа. Запишите его в базу данных в проверку (поле status_code)
- [x] Выведите код последней проверки в списке сайтов
- [x] Выведите код ответа в списке проверок конкретного сайта
- [ ] Задеплойте результат

Req-s:
- [x] При выполнении запросов должна выполняться обработка исключений
- [x] Обратите внимание, что при этом проверка не создается и выводится flash-сообщение 'Произошла ошибка при проверке'
- [x] Для запроса к сайту используйте библиотеку requests
- [x] Для проверки статуса страницы используйте Response.raise_for_status()
- [x] Если произошла ошибка, то проверка не добавляется в список проверок

