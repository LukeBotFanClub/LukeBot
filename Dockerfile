FROM python:3.10-slim

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git curl gcc libffi-dev
RUN python3 -m pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3 -; exit 0
RUN cat *.log
RUN export PATH="/root/.local/bin:$PATH"
RUN echo $PATH
COPY . .

RUN /root/.local/bin/poetry install --no-dev

CMD start-lukebot
