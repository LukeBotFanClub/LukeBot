FROM ubuntu:20.04

RUN apt-get update && apt-get upgrade
RUN apt-get install -y git python3.10 python3-pip

COPY . .

RUN python3 -m pip install --upgrade pip
RUN python3 -vv -m pip install .

CMD start-lukebot
