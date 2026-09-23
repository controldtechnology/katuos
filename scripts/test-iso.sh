#!/bin/bash
set -Eeuo pipefail
exec python3 "$(dirname "$0")/test_iso.py" "$@"
