#!/bin/bash
set -Eeuo pipefail
exec python3 "$(dirname "$0")/build-package.py" "$@"
