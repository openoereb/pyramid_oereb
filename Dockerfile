FROM python:3.12-bullseye

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

RUN pip install -r requirements.txt -r tests-requirements.txt -r dev-requirements.txt

# keep container running until killed - For DEV use only
CMD [ "pserve", "development.ini", "--reload"]
