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

```bash
$ git clone https://github.com/ivekhov/python-project-83.git
$ make install
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

- [ ] Создайте БД развернутого приложения (на сайте render)

- [x] Создайте в базе данных таблицу urls с полями id, name и created_at

- [x] В корне проекта создайте SQL-файл с таблицей и назовите его database.sql

- [x] Реализуйте форму ввода адреса на главной странице и обработчик, который добавляет введенную информацию в базу данных

- [x] Не забудьте, что имя поля ввода input должно быть url

- [x] Реализуйте валидацию для введенного URL-адреса. У URL обязательно должен быть валидный адрес, не превышающий 255 символов

- [x] Реализуйте вывод конкретного введенного URL на отдельной странице urls/<id>

- [x] Реализуйте вывод всех добавленных URL на отдельной странице /urls и проверьте, что новые записи отображаются первыми

- [x] Настройте рендеринг таблицы сайтов с помощью Bootstrap (см пример https://python-page-analyzer-ru.hexlet.app/urls )

- [x] Настройте рендеринг страницы отдельного сайта с помощью Bootstrap (https://python-page-analyzer-ru.hexlet.app/)

- [ ] Настройте рендеринг flash-сообщений с помощью Bootstrap

- [ ] Задеплойте результат


### Требования
- [x] Используйте именованный роутинг
- [x] Помните, что имена сайтов должны быть уникальны. Добавление сайта с тем же именем не должно приводить к созданию новой записи в базе данных
- [ ] Если данные не прошли валидацию, то должна рендериться форма с выводом ошибки
- [x] Используйте flash-сообщения для оповещения об успешном добавлении или ошибках
- [ ] Используйте только стандартные возможности Bootstrap: Сетка, Компоненты, Утилиты
- [ ] Проверьте, что значения атрибутов HTML-элементов форм, текст элементов Label форм, тексты кнопок и ссылок для перехода по страницам, flash-сообщения и другие тексты точно соответствуют демонстрационному проекту
- [ ] У таблицы со списком адресов должен быть атрибут data-test="urls"
- [ ] У таблицы с информацией об адресе должен быть атрибут data-test="url"
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


## Starting:
```bash

# If port 8080 is in use, kill it:
lsof -ti :8080 | xargs kill -9

# start server:
poetry run gunicorn -w 5 -b 0.0.0.0:8080 page_analyzer:app
```

    