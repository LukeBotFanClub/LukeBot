FROM python:3.10-slim

RUN apt-get update && apt-get upgrade
RUN apt-get install -y git

COPY . .

RUN python3 -m pip install --upgrade pip
RUN python3 -vv -m pip install .

CMD start-lukebot
