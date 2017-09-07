#!/bin/bash -ex

# Build the project
make install

# Prepare .pypirc config
echo "[distutils]" > ~/.pypirc
echo "index-servers = pypi" >> ~/.pypirc
echo "[pypi]" >> ~/.pypirc
echo "repository:https://upload.pypi.org/legacy/" >> ~/.pypirc
echo "username:${TRAVIS_USERNAME}" >> ~/.pypirc
echo "password:${TRAVIS_PASSWORD}" >> ~/.pypirc

# Deploy daily pypi build
python setup.py egg_info --tag-date --tag-build=dev sdist bdist_wheel upload -r pypi
