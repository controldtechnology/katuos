#!/bin/bash
set -Eeuo pipefail
# Use dch for valid Debian dates/format; never infer a release version from Git.
[[ $# -ge 2 ]] || { echo 'Usage: generate-changelog.sh PACKAGE VERSION [message]' >&2; exit 2; }
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
[[ $1 =~ ^katu-[a-z0-9+-]+$ && $2 =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]
exec dch --changelog "$ROOT/packages/$1/DEBIAN/changelog" --newversion "$2" --distribution beta "${3:-Component update; describe before publishing}"
