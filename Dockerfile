FROM python:3.10-slim

ENV GG_TOKEN
ENV DISCORD_TOKEN
ENV DISCORD_CHANNEL_ID

COPY . .

RUN pip install -r requirements.txt

CMD python3 ./luke_bot/__init__.py
