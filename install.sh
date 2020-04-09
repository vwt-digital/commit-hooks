#!/bin/bash
#
# Installing commit hooks, depending on your operating system.
#

echo "Installing commit hooks..."

hook_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ $hook_branch == "develop" ]]; then
  echo -e "\e[33mWARNING: You are installing while on develop branch. This branch might not be entirely stable. Use" \
          "the master branch for more stable and secure hooks.\e[0m"
fi
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Installing SAST-scan..."
if ! docker pull eu.gcr.io/vwt-p-gew1-dat-cloudbuilders/cloudbuilder-sast:latest; then
  echo -e "\e[1;31mError: Install wasn't executed with sufficient permissions or Docker is not configured for gcloud." \
          "You might need to run 'gcloud auth configure-docker' to configure Docker. \e[0m"
fi
if ! docker pull eu.gcr.io/vwt-d-gew1-dat-cloudbuilders/cloudbuilder-sast:latest; then
  echo -e "\e[1;31mError: Install wasn't executed with sufficient permissions or Docker is not configured for gcloud." \
          "You might need to run 'gcloud auth configure-docker' to configure Docker. \e[0m"
fi

git config --global core.hooksPath "${DIR}"/hooks
echo "Configured global core.hooksPath: ${DIR}/hooks"
