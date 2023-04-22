FROM python:3.10-alpine

WORKDIR /opt

COPY poetry.lock pyproject.toml ./

RUN pip install poetry \
    && poetry config virtualenvs.create false\
    && poetry install --without dev --no-root

COPY . .

ENTRYPOINT sh entrypoint.sh
