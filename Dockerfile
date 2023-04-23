ARG PYTHON_VERSION="3.11"
FROM ghcr.io/lukebotfanclub/poetry-python:${PYTHON_VERSION} as requirements-stage

WORKDIR /tmp

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes;poetry export --with dev -f requirements.txt --output dev-requirements.txt --without-hashes


FROM python:${PYTHON_VERSION}-slim

WORKDIR /code
RUN apt-get update && apt-get -y upgrade && apt-get install gcc -y

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
COPY --from=requirements-stage /tmp/dev-requirements.txt /code/dev-requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

CMD python3 -m luke_bot
