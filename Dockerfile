FROM python:3.10-slim

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git curl gcc
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY . .

RUN /root/.local/bin/poetry install --no-dev

CMD /root/.local/bin/poetry run start-lukebot
