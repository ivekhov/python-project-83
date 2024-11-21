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