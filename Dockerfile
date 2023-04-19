FROM python:3.10 as requirements-stage

WORKDIR /tmp

RUN --mount=type=tmpfs,target=/root/.cargo \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    . $HOME/.cargo/env && \
    pip install "poetry>=1.3,<2.0"

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes;poetry export --with dev -f requirements.txt --output dev-requirements.txt --without-hashes


FROM python:3.10-slim

WORKDIR /code
RUN apt-get update && apt-get -y upgrade && apt-get install gcc -y

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
COPY --from=requirements-stage /tmp/dev-requirements.txt /code/dev-requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

CMD python3 -m luke_bot
