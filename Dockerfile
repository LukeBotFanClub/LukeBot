FROM python:3.10-slim
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.14

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git gcc
RUN pip install "poetry==$POETRY_VERSION"

COPY . .

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi


CMD poetry run start-lukebot
