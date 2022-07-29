FROM python:3.10-slim

COPY . .

RUN pip install -r requirements.txt

CMD python3 ./luke_bot/__init__.py
