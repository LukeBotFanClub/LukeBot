FROM python:3.10-slim

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git curl gcc
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 - --version 1.1.14

COPY . .

RUN $HOME/.poetry/bin/poetry install --no-dev

CMD $HOME/.poetry/bin/poetry run start-lukebot
