FROM camptocamp/c2cwsgiutils:3
LABEL maintainer "info@camptocamp.org"

WORKDIR /app
ARG DEV_PACKAGES="libgeos-c1v5 libpq-dev"
ARG PYTHON_DEV_PACKAGES="python3.7-dev build-essential"

# The full pdf extract functionality requires pdftk, but this library is not available in Ubuntu bionic.
# Note that it is expected that the full pdf extract functionality will be removed from the next
# specification.
#RUN \
#    apt-get update && \
#    apt-get install --assume-yes --no-install-recommends pdftk-java && \
#    apt-get clean && \
#    rm --recursive --force /var/lib/apt/lists/*

COPY docker/requirements.txt /app/docker/
COPY requirements.txt /app/

RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install --yes --no-install-recommends \
        ${DEV_PACKAGES} ${PYTHON_DEV_PACKAGES} && \
    pip install --disable-pip-version-check --no-cache-dir --requirement requirements.txt --requirement docker/requirements.txt && \
    apt remove --purge --autoremove --yes ${PYTHON_DEV_PACKAGES} binutils && \
    apt-get clean && \
    rm --force --recursive /var/lib/apt/lists/*

COPY . /app

RUN pip install --disable-pip-version-check --no-cache-dir --editable . && \
    mv docker/config.yaml.tmpl . && \
    mv docker/production.ini.tmpl .

ENV LOGO_CANTON=logo_canton.png \
    DEVELOPMENT=false \
    LOG_LEVEL=INFO

COPY docker/bin/* /usr/bin/

RUN apt update && \
    apt install --yes --no-install-recommends gettext-base

ENTRYPOINT ["eval-templates", "c2cwsgiutils_run"]
