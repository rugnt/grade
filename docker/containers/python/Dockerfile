FROM python:3.10-alpine3.19

ARG APP_ENV='prod'
ARG APP_ENV=${APP_ENV}
ENV APP_ENV ${APP_ENV}

ARG USER_ID='1000'
ARG USER_ID=${USER_ID}
ENV USER_ID ${USER_ID}

ARG GROUP_ID='1000'
ARG GROUP_ID=${GROUP_ID}
ENV GROUP_ID ${GROUP_ID}

ARG PIP_ROOT_USER_ACTION='ignore'
ARG PIP_ROOT_USER_ACTION=${PIP_ROOT_USER_ACTION}
ENV PIP_ROOT_USER_ACTION ${PIP_ROOT_USER_ACTION}

ARG POETRY_VIRTUALENVS_CREATE='false'
ARG POETRY_VIRTUALENVS_CREATE=${POETRY_VIRTUALENVS_CREATE}
ENV POETRY_VIRTUALENVS_CREATE ${POETRY_VIRTUALENVS_CREATE}

RUN apk --no-cache add shadow bash gcc g++ musl-dev python3-dev libffi-dev make curl

COPY ./pyproject.toml .
COPY ./poetry.lock .
RUN pip install -U pip
RUN pip install poetry==1.7.0
# RUN poetry install --no-root --without dev,test  FOR PROD
RUN poetry install --no-root

RUN useradd -u $USER_ID -g www-data -s /bin/bash -d /usr/src/app www-data && mkdir -p /usr/src/app && chown www-data.www-data /usr/src/app
USER www-data

WORKDIR /usr/src/app
