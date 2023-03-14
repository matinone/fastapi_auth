[![Testing](https://github.com/mbrignone/todos_api/actions/workflows/python-app.yml/badge.svg)](https://github.com/mbrignone/todos_api/actions/workflows/python-app.yml)

# User Authentication with FastAPI

Complete user authentication support, with sample endpoints to handle users and create items in a per user ToDo list.

## Features

- User registration and login using username (email) and password (OAuth2) to create the user and generate access tokens.
- User registration and login using Google credentials to create the user and generate access tokens.
- Email account verification and password recovery.
- Refresh tokens support.
- Protected endpoints.
- Interactive API documentation (provided by Swagger UI).
- 100% test coverage (`app/api/`).
- Python formatting and styling using black, isort and flake8.
- Frontend using Vue available [here](https://github.com/mbrignone/tasks_app/).

## Technologies / frameworks / tools

- [FastAPI](https://fastapi.tiangolo.com/).
- [SQLite](https://www.sqlite.org/index.html).
- [PostgreSQL](https://www.postgresql.org/about/).
- [SQLAlchemy](https://www.sqlalchemy.org/).
- [Pytest](https://docs.pytest.org/en/7.1.x/).
- [Factory Boy](https://factoryboy.readthedocs.io/en/stable/).
- [Docker](https://www.docker.com/).
- [Kubernetes](https://kubernetes.io/).
- [Black](https://black.readthedocs.io/en/stable/).
- [Isort](https://pycqa.github.io/isort/).
- [Flake8](https://flake8.pycqa.org/en/latest/index.html).
- [Pre-commit hook](https://pre-commit.com/).
- [Github Actions](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python).

## Running it locally

With or without Docker, the proper environment variables must be set before running the server. They can be externally set or a `.env` file can be used (see `example.env` for reference). All the env variables have reasonable default values.

The following commands must be run from the top level directory.

### Without Docker

Locally, the environment variable `ENVIRONMENT` must be set to `test`, to use SQLite instead of PostgreSQL.

```
$ pip install -r requirements.txt
$ ENVIRONMENT=test uvicorn app.main:app
```

The server is now running at `http://127.0.0.1:8000`. The interactive API docs can be accessed from `http://127.0.0.1:8000/docs`.

### With Docker

```
$ docker compose up -d
```

The server is now running at `http://127.0.0.1:80`. The interactive API docs can be accessed from `http://127.0.0.1:80/docs`. The pgAdmin platform can be accessed from `http://127.0.0.1:5050`, using `email = pgadmin4@pgadmin.org` and `password = admin` to login (they are defined in the `docker-compose.yml` file).

### With Kubernetes

To run the app in a single-node local Kubernetes cluster (using [minikube](https://minikube.sigs.k8s.io/docs/start/)), it is first required to update the existing YAML files in the `/kubernetes` directory:

- Change the value of `spec.template.spec.containers.image` of the `Deployment` resource definition in `fastapi_app.yaml`, to use your own uploaded image in [Docker Hub](https://hub.docker.com/).
- Set the path that will be used in the local machine to persist the database data, updating the value of `spec.hostPath.path` of the `PersistentVolume` resource definition in `postgres_db.yaml`.

Once the files have been updated, the following commands must be run to start the cluster and apply the desired configuration:

```bash
$ cd kubernetes
$ minikube start
$ kubectl apply -f=environment.yaml
$ kubectl apply -f=postgres_db.yaml
$ kubectl apply -f=fastapi_app.yaml
```

If all the resources are successfully created, then the command `$ minikube service fastapi-service` can be used to get the URL to access the app.

Finally, the command `$ minikube delete --all` can be used to delete the whole cluster.

## Running tests

The following commands must be run from the top level directory.

```
$ pip install -r requirements.txt
$ pip install -r dev_requirements.txt
$ python -m pytest app/tests/ -v --cov=app/api
```
