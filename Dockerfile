FROM python:3.10-slim

COPY . .

RUN pip install .

CMD start-lukebot
