#!/bin/bash
set -e

mkdir -p /home/pkg/
cp -r /python-ovh/ /home/pkg/src
cd /home/pkg/src

export DEBIAN_FRONTEND="noninteractive"
apt-get update
# Add basic packages
apt-get install -y ca-certificates apt-transport-https

# Build package tooling
apt-get -yq install procps build-essential devscripts quilt debhelper
apt-get -yq install dh-systemd


DEBUILD_OPTIONS=--buildinfo-option=-O

mkdir -p /home/pkg/src/ovh
if [ ! -f /home/pkg/src/ovh/bbb ] && [ ! -f /home/pkg/src/ovh/build ]; then
    echo "INFO: BuildBot is creating an executable file in ovh/bbb"
    mkdir -p /home/pkg/src/ovh
    cat > /home/pkg/src/ovh/bbb << EOF
set -e
debuild $DEBUILD_OPTIONS -us -uc -b -j$(nproc)
EOF

	cat /home/pkg/src/ovh/bbb
	chmod +x /home/pkg/src/ovh/bbb
fi

echo "BUILDBOT> Prepare the build process with Debian build dependencies (if debian/control file exists)"
if [ -f /home/pkg/src/debian/control ]; then
    mk-build-deps -r -t "apt-get --no-install-recommends -y" -i /home/pkg/src/debian/control
else
    echo "INFO: /home/pkg/src/debian/control is absent...skipping mk-build-deps"
fi
if [ -f /home/pkg/src/ovh/bbb ]; then
    echo "BUILDBOT> Starting the build process via /home/pkg/src/ovh/bbb"
    cd /home/pkg/src && ./ovh/bbb
elif [ -f /home/pkg/src/ovh/build ]; then
    echo "BUILDBOT> Starting the build process via /home/pkg/src/ovh/build"
    cd /home/pkg/src && ./ovh/build
fi

echo "BUILDBOT> Moving output to the artifact directory"
cd /home/pkg && find . -maxdepth 1 -type f -print -exec mv '{}' /output/ \;
chown -R 1000:1000 /output/
