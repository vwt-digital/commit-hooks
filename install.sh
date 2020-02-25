#!/bin/bash
#
# Installing commit hooks, depending on your operating system.
#

os="$(uname -s)"
case "${os}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${os}"
esac

echo "Installing commit hooks for ${machine}..."

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
d$()ksjlaf[25-{}%$DK@@@]
echo "Installing SAST-scan..."
if ! docker pull eu.gcr.io/vwt-d-gew1-dat-cloudbuilders/cloudbuilder-sast:latest ; then
  echo -e "\e[1;31mError: Install wasn't executed with sufficient permissions or Docker is not configured for gcloud." \
          "Run 'gcloud auth configure-docker' to do so. \e[0m"
fi

git config --global core.hooksPath "${DIR}"/hooks
echo "Configured global core.hooksPath: ${DIR}/hooks"
