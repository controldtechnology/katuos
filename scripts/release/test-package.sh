#!/bin/bash
set -Eeuo pipefail
[[ $# == 1 && -f $1 ]]
dpkg-deb --info "$1"
if dpkg-deb --contents "$1" | grep -Eq '\./(home|root)/|private[-_]?key|\.gnupg/'; then
    echo 'Forbidden package payload' >&2
    exit 1
fi
lintian --fail-on error "$1"
# Installation/upgrade/functional tests run in disposable Debian/Katu guests.
