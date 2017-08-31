#!/bin/bash -ex

docker login --username ${DOCKER_USERNAME} --password ${DOCKER_PASSWORD}

if [ "${TRAVIS_EVENT_TYPE}" = "cron" ]
then
    docker push camptocamp/pyramid-oereb:latest
fi

if [ "${TRAVIS_TAG}" != "" ]
then
    docker tag camptocamp/pyramid-oereb:latest camptocamp/pyramid-oereb:${TRAVIS_TAG}
    docker push camptocamp/pyramid-oereb:${TRAVIS_TAG}
fi
