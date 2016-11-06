#!/bin/bash

# an example script that will build a virtual environment in the build directory, install the current project
# (using setup.py install) and then package it. the output deb path is written to a known location and then can be
# read by an upload script

set -e

export VENV_NAME=example-virtualenv
export VENV_DIR=build/${VENV_NAME}
export VENV_BIN_DIR=${VENV_DIR}/bin
export VENV_VERSION=1.0
export PYTHON_VERSION=3.5

rm -r ${VENV_DIR} || true
virtualenv -p `which python${PYTHON_VERSION}` --no-site-packages ${VENV_DIR}
${VENV_BIN_DIR}/python setup.py install
virtualenv --relocatable ${VENV_DIR}
constrictor-build -p venv-config.json > build/venv-output-path
