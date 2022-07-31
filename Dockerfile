FROM python:3.10-slim

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git curl
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -; exit 0
RUN cat *.log
RUN export PATH="/root/.local/bin:$PATH"
RUN echo $PATH
COPY . .

RUN /root/.local/bin/poetry install --no-dev

CMD start-lukebot
