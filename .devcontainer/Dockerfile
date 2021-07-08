FROM python:3.7-buster

ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUALENV_PYTHON=/usr/bin/python3.7

ARG DEV_PACKAGES="python3.7-dev build-essential libgeos-dev"

RUN apt-get update && \
  apt-get install --yes --no-install-recommends \
    python3-pip \
    python3-venv \
    virtualenv \
    ${DEV_PACKAGES} \
    postgresql-client
