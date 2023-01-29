FROM python:3.10-slim
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.14

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git curl gcc
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 - --version $POETRY_VERSION


WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN $HOME/.poetry/bin/poetry config virtualenvs.create false \
  && $HOME/.poetry/bin/poetry install --no-dev --no-interaction --no-ansi

COPY . /code

CMD python3 -m luke_bot
