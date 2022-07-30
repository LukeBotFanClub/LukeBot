FROM python:3.10-slim

RUN apt-get install -y git # apk add git

COPY . .

RUN python3 -m pip install --upgrade pip && pip install .

CMD start-lukebot
