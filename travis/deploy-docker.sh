#!/bin/bash -ex

docker login --username ${DOCKER_USERNAME} --password ${DOCKER_PASSWORD}
docker login ghcr.io --username ${GITHUB_USERNAME} --password ${GITHUB_TOKEN}

if [ "${TRAVIS_EVENT_TYPE}" = "cron" ]
then
    docker tag openoereb/pyramid-oereb:latest camptocamp/pyramid-oereb:latest
    docker push camptocamp/pyramid-oereb:latest
    docker tag openoereb/pyramid-oereb:latest ghcr.io/openoereb/pyramid-oereb/pyramid-oereb:latest
    docker push ghcr.io/openoereb/pyramid-oereb/pyramid-oereb:latest
fi

if [ "${TRAVIS_TAG}" != "" ]
then
    docker tag openoereb/pyramid-oereb:latest camptocamp/pyramid-oereb:${TRAVIS_TAG}
    docker push camptocamp/pyramid-oereb:${TRAVIS_TAG}
    docker tag openoereb/pyramid-oereb:latest ghcr.io/openoereb/pyramid-oereb/pyramid-oereb:${TRAVIS_TAG}
    docker push ghcr.io/openoereb/pyramid-oereb/pyramid-oereb:${TRAVIS_TAG}
fi
