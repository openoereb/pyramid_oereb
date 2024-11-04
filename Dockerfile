FROM python:3.13.0-bullseye

ENV DEBIAN_FRONTEND=noninteractive

ARG DEV_PACKAGES="build-essential"

RUN apt-get update && \
  apt-get install --yes --no-install-recommends \
  ${DEV_PACKAGES} \
  zsh \
  vim \
  xsltproc \
  postgresql-client

ENV SHELL /bin/zsh

RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

RUN mkdir /venvs && \
  chmod a+w /venvs/

RUN mkdir /workspace && \
  chmod a+w /workspace/

COPY . /workspace/

WORKDIR /workspace

# keep container running until killed - For DEV use only
CMD [ "pserve", "development.ini", "--reload"]
