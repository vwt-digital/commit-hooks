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
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

echo "Installing SAST-scan..."
if ! docker pull eu.gcr.io/vwt-p-gew1-dat-cloudbuilders/cloudbuilder-sast:latest; then
  echo -e "\e[1;31mError: Install wasn't executed with sufficient permissions or Docker is not configured for" \
    "gcloud\e[0m"
else
  docker pull eu.gcr.io/vwt-d-gew1-dat-cloudbuilders/cloudbuilder-sast:latest
fi

echo "Cloning schemavalidator"
git clone https://github.com/vwt-digital/schema-validator.git
if [[ $hook_branch == "master" ]]; then
  cd schema-validator &&
  git checkout origin/master &&
  cd ..
fi
target_dir=./hooks/schema-conform-meta-schema
if [ -d $target_dir ]; then
  rm -rf $target_dir
fi
cp -rf ./schema-validator/commit-hooks/schema-conform-meta-schema $target_dir &&
cp -rf ./schema-validator/general-functions/fill-references-in-schemas/fill_refs_schema_locally.py $target_dir/fill_refs_schema.py &&
rm -rf schema-validator

echo "Installing python virtualenv"
python3 -m pip install --user virtualenv

pip install black
pip install isort

git config --global core.hooksPath "${DIR}"/hooks
echo "Configured global core.hooksPath: ${DIR}/hooks"
