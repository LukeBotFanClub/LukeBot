FROM python:3.10-alpine

RUN apk update && apk upgrade
RUN apk add -f git

COPY . .

RUN python3 -m pip install --upgrade pip
RUN python3 -vv -m pip install .

CMD start-lukebot
