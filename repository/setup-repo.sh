#!/bin/bash
set -Eeuo pipefail
# Compatibility entry point: authenticated channels only.
exec python3 "$(dirname "$0")/../scripts/release/repository.py" "$@"
