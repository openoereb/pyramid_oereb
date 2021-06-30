FROM python:3.7-buster

USER 0

ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUALENV_PYTHON=/usr/bin/python3.7
ENV PGPASSWORD=postgres

ARG DEV_PACKAGES="python3.7-dev build-essential libgeos-dev"

RUN apt-get update && \
  apt-get install --yes --no-install-recommends \
    python3-pip \
    python3-venv \
    virtualenv \
    ${DEV_PACKAGES} \
    postgresql-client

RUN groupadd -g 1000 vscode && \
    useradd --home-dir /home/vscode --shell /bin/bash -g vscode -u 1000 vscode

USER 501
