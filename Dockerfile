FROM python:3.10-slim

ENV POETRY_VERSION=1.1.14

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git curl gcc
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 - --version $POETRY_VERSION

COPY . .

RUN $HOME/.poetry/bin/poetry install --no-dev --no-interaction --no-ansi


CMD $HOME/.poetry/bin/poetry run start-lukebot