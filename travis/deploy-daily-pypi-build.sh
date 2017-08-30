#!/bin/bash

# Prepare .pypirc config
echo "[distutils]" > ~/.pypirc
echo "index-servers = pypi" >> ~/.pypirc
echo "[pypi]" >> ~/.pypirc
echo "repository:https://upload.pypi.org/legacy/" >> ~/.pypirc
echo "username:${TRAVIS_USERNAME}" >> ~/.pypirc
echo "password:${TRAVIS_PASSWORD}" >> ~/.pypirc

# Deploy daily pypi build
.venv/bin/python setup.py egg_info --tag-date --tag-build=dev sdist upload -r pypi
