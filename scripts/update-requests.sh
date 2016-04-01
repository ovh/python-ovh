#!/bin/bash
#
# Usage: ./scripts/update-requests.sh <version>
#

set -e

VERSION="$1"

if [ -z "$VERSION" ]
then
    echo "Usage: ./scripts/update-requests.sh <version (git tag)>" >&2
    exit 1
fi

# Move to project root
cd "$(dirname "$0")"/..

# Upgrade
cd ovh/vendor

echo "Cleaning old installation..."
rm -rf requests

echo "Downloading version $VERSION..."
wget -q "https://github.com/kennethreitz/requests/archive/$VERSION.tar.gz" -O ./tmp-requests.tar.gz

echo "Installing..."
tar -xzf ./tmp-requests.tar.gz
mv requests-*/requests ./requests

echo "Cleaning temporary files..."
rm -rf ./tmp-requests.tar.gz requests-*

echo "All done!"

