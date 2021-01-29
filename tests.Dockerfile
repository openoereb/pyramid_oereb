FROM camptocamp/c2cwsgiutils:3
LABEL maintainer "info@camptocamp.org"

WORKDIR /app

RUN apt update && \
    apt install --yes python3.6-dev python3.7-dev python3.8-dev build-essential libgeos-c1v5 && \
    pip install --no-cache-dir tox && \
    apt-get clean && \
    rm --force --recursive /var/lib/apt/lists/*

COPY . /app
