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

if [ "$machine" = "Linux" ]; then
    echo "Installing packages for ${machine}..."
    echo "Installing shellcheck..."
    apt-get install -y shellcheck
    echo "Installing bandit..."
    pip3 install bandit
elif [ "$machine" = "Mac" ]; then
    echo "Installing packages for ${machine}..."
    brew install shellcheck
fi

git config --global core.hooksPath "${DIR}"/hooks
echo "Configured global core.hooksPath: ${DIR}/hooks"

echo "Installing other required packages for git hooks..."
if ! command -v flake8; then
  echo "Installing flak8..."
  pip3 install flake8
fi
