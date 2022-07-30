FROM python:3.10-slim

RUN apt-get update && apt-get upgrade
RUN apt-get install -y git python3-dev

COPY . .

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install .

CMD start-lukebot
