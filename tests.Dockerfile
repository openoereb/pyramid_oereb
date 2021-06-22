FROM camptocamp/c2cwsgiutils:3
LABEL maintainer "info@camptocamp.org"

WORKDIR /app

RUN apt update && \
    apt install --yes --no-install-recommends build-essential

COPY requirements.txt requirements-tests.txt /app/

ARG DEV_PACKAGES="libgeos-c1v5 libpq-dev"
ARG PYTHON_TEST_VERSION
ENV PYTHON_DEV_PACKAGE=${PYTHON_TEST_VERSION}-dev
RUN apt update && \
    apt install --yes ${PYTHON_DEV_PACKAGE} ${DEV_PACKAGES} && \
    ${PYTHON_TEST_VERSION} -m pip install  --disable-pip-version-check --no-cache-dir --requirement requirements.txt --requirement requirements-tests.txt && \
    apt-get clean && \
    rm --force --recursive /var/lib/apt/lists/*

COPY . /app
