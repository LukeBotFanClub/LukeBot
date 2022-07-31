FROM python:3.10-slim

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git curl
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
RUN export PATH="$HOME/.poetry/bin:$PATH"

COPY . .

RUN poetry install

CMD start-lukebot
