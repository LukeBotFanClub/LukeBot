FROM python:3.9 as requirements-stage

WORKDIR /tmp

RUN pip install "poetry>=1.3,<2.0"

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN poetry export --with dev -f requirements.txt --output dev-requirements.txt --without-hashes


FROM python:3.9-slim

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
COPY --from=requirements-stage /tmp/dev-requirements.txt /code/dev-requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

CMD python3 -m luke_bot
