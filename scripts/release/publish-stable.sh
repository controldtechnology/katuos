#!/bin/bash
set -Eeuo pipefail
exec python3 "$(dirname "$0")/repository.py" publish stable "$@"
