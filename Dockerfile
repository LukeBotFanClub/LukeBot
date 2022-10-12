FROM python:3.10-slim

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git curl gcc
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY . .

RUN $HOME/.poetry/bin/poetry install --no-dev

CMD $HOME/.poetry/bin/poetry run start-lukebot
