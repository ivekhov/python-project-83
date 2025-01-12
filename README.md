# Project 3 "Page Analyzer"

**Part of Python Developer Profession on Hexlet**
https://hexlet.io/programs/python


## About tool

Page Analyzer


## Public web-page:

https://python-project-83-rr2w.onrender.com/


---

### Hexlet tests and linter status:

[![Actions Status](https://github.com/ivekhov/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/ivekhov/python-project-83/actions)


----
## How to

Install project: 
```bash
$ git clone https://github.com/ivekhov/python-project-83.git
$ cd python-project-83
$ make install
```

First time setup:

```bash:
# of server is running locally, export env variable
$ export DATABASE_URL="postgresql://{user}:{mypassword}@localhost:5432/mydb"
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

# or if port is in use, kill it:
$ make stop & make start

```

If Postgres is running in Docker:

```bash
$ docker exec -it postgres-container psql -U postgres -d hexlet
```

----

## Repo Example from Hexlet

https://github.com/hexlet-components/python-flask-example/tree/database



-------------

## Docker comamnds


```bash

# connect to postgres container and run psql shell for selects 
$ docker exec -it postgres-container psql -U postgres -d hexlet

# execute sql file from machine to docker container directly
$ docker exec -it postgres-container psql -U postgres -d hexlet -f ./home/docker_database_init.sql

# copy file to container
$ docker cp docker_database_init.sql  postgres-container:/home/docker_database_init.sql

# conect to container in bash mode
$ docker exec -it postgres-container bash

# run sql script inside contatiner
$ psql -U postgres -d hexlet -f docker_database_init.sql

```

For uploading data from script inside docker : from machine to docker

```sql
-- in .sql file
COPY urls(name) 
FROM './tests/fixtures/database.csv' 
DELIMITER ','
CSV HEADER;
```

## Postgres local

Starting service via pgadmin


Connection to local postgres db 

``` bash
$ psql -U postgres -d page_analyzer 
# pass in .env

```






-------------

