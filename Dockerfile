FROM alpine:3.15

RUN apk update && apk upgrade
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 py3-pip python3-dev && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

COPY . .

RUN python3 -m pip install --upgrade pip
RUN python3 -vv -m pip install .

CMD start-lukebot
