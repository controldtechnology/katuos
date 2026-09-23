#!/bin/bash
set -Eeuo pipefail
exec bash "$(dirname "$0")/build-clean.sh" "$@"
