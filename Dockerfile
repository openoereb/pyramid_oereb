FROM camptocamp/c2cwsgiutils:0
LABEL maintainer "info@camptocamp.org"

WORKDIR /app

COPY docker/requirements.txt /app/docker/
COPY requirements.txt /app/

RUN pip install --disable-pip-version-check --no-cache-dir --requirement requirements.txt --requirement docker/requirements.txt

COPY . /app

RUN pip install --disable-pip-version-check --no-cache-dir --editable . && \
    mkdir /etc/pyramid_oereb && \
    mv docker/config.yaml /etc/pyramid_oereb/ && \
    mv docker/production.ini .

ENV LOGO_CANTON=logo_canton.png \
    DEVELOPMENT=false \
    LOG_LEVEL=INFO
