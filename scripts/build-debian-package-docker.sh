#!/bin/bash
set -euo pipefail

exec docker run -it --rm --name python-ovh-debian-builder -v python-ovh-debian-builder-output:/output -v "${PWD}:/python-ovh:ro" debian:buster /python-ovh/scripts/build-debian-package-recipe.sh
