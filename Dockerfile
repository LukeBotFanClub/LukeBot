FROM python:3.10-slim

RUN apt-get update && apt-get upgrade && apt-get install -y git

COPY . .

RUN python3 -m pip install --upgrade pip && pip install .

CMD start-lukebot
