FROM python:3.10-alpine

RUN apk add git

COPY . .

RUN python3 -m pip install --upgrade pip && pip install .

CMD start-lukebot
