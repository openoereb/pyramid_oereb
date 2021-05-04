FROM camptocamp/c2cwsgiutils:release_4
LABEL maintainer "info@camptocamp.org"

WORKDIR /app
ARG DEV_PACKAGES="python3.8-dev build-essential libgeos-dev"

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
        libgeos-c1v5 ${DEV_PACKAGES} && \
    pip3 install --disable-pip-version-check --no-cache-dir --requirement requirements.txt --requirement docker/requirements.txt && \
    apt remove --purge --autoremove --yes ${DEV_PACKAGES} binutils && \
    apt-get clean && \
    rm --force --recursive /var/lib/apt/lists/*

COPY . /app

RUN pip3 install --disable-pip-version-check --no-cache-dir --editable . && \
    mkdir /etc/pyramid_oereb && \
    mv docker/config.yaml /etc/pyramid_oereb/ && \
    mv docker/production.ini.tmpl .

ENV LOGO_CANTON=logo_canton.png \
    DEVELOPMENT=false \
    LOG_LEVEL=INFO

COPY docker/bin/* /usr/bin/

RUN apt update && \
    apt install --yes --no-install-recommends gettext-base

ENTRYPOINT ["eval-templates", "c2cwsgiutils-run"]