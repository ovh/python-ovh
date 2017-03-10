#!/bin/bash
#
# Usage: ./scripts/bump-version.sh <version>
#

set -e

VERSION="$1"
CURRENT_VERSION="$(git describe --tags --abbrev=0 | grep -o '[.0-9]*')"
CURRENT_VERSION_EXP="$(echo $CURRENT_VERSION | sed 's/\./\\./g')"

if ! [[ "${VERSION}" != "" && "${VERSION}" =~ ^[.0-9]*$ ]]
then
    echo "Usage: ./scripts/bump-version.sh <version (a.b.c)>" >&2
    echo "Current version: ${CURRENT_VERSION}"
    exit 1
fi

# Move to project root
cd "$(dirname "$0")"/..

# Edit version number in files
grep -rlI "${CURRENT_VERSION_EXP}" | grep -vP '(^\.git|CHANGELOG\.md)' | xargs sed -i "s/${CURRENT_VERSION_EXP}/${VERSION}/g"

# Prepare Changelog
CHANGES=$(git log --oneline --no-merges v${CURRENT_VERSION}.. | sed 's/^[a-f0-9]*/ -/g' | sed ':a;N;$!ba;s/\n/\\n/g')

if [ -z "${CHANGES}" ]
then
    echo "Ooops, no changes detected since last version (${CURRENT_VERSION})"
    exit 1
fi

sed -i "4i## ${VERSION} ($(date --iso))\n${CHANGES}\n" CHANGELOG.md
vim CHANGELOG.md

# Upgrading debian/changelog
dch --noquery --distribution trusty --newversion ${VERSION} "New upstream release v${VERSION}"
awk "/## ${VERSION}/{f=1;next}/##/{f=0} f" CHANGELOG.md | sed 's/^\s*-\s*//' | while IFS= read -r line ; do
    dch --noquery --distribution trusty -a "$line"
done

# Commit and tag
git commit -sam "[auto] bump version to v${VERSION}"
git tag v${VERSION}

echo "All done!"

