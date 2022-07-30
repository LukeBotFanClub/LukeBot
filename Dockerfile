FROM python:3.10-slim

COPY . .
RUN ls -a

RUN python3 -m pip install --upgrade pip && pip install .

CMD start-lukebot
