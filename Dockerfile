FROM python:3.7-buster

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /workspace

COPY requirements.txt /workspace
COPY requirements-tests.txt /workspace

RUN apt-get update && \
  apt-get install --yes --no-install-recommends \
    python3-pip \
    python3-venv \
    virtualenv \
    python3.7-dev \
    build-essential \
    libgeos-dev \
    postgresql-client

RUN python3 -m venv /workspace/.venv && \
  /workspace/.venv/bin/pip3 install --upgrade pip && \
  /workspace/.venv/bin/pip3 install -r requirements.txt -r requirements-tests.txt
