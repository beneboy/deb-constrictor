#!/bin/bash

# an example of building using constrictor-build and build-config.json, then uploading to a directory
# being watched by reprepro

set -e

APT_HOST="apt.example.com"
APT_SSH_USER="apt"
APT_UPLOAD_DIRECTORY="/srv/www/repos/apt/ubuntu/incoming/"

PACKAGE_OUTPUT_PATH=$(constrictor-build -p)
PACKAGE_NAME=$(basename ${PACKAGE_OUTPUT_PATH})

PACKAGE_UPLOAD_PATH="/srv/www/repos/apt/ubuntu/incoming/${PACKAGE_NAME}"
PACKAGE_UPLOAD_PATH_TMP="${PACKAGE_UPLOAD_PATH}.tmp"

scp ${PACKAGE_OUTPUT_PATH} ${APT_SSH_USER}@${APT_HOST}:${PACKAGE_UPLOAD_PATH_TMP}
ssh ${APT_SSH_USER}@${APT_HOST} "mv ${PACKAGE_UPLOAD_PATH_TMP} ${PACKAGE_UPLOAD_PATH}"