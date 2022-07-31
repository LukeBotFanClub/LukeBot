FROM python:3.10-slim

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git curl
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN export PATH="$HOME/.poetry/bin:$PATH"

COPY . .

RUN poetry install

CMD start-lukebot
