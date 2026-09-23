#!/bin/bash
set -Eeuo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
[[ $# -ge 1 ]] || { echo "Usage: $0 ISO [REPORT.json]" >&2; exit 2; }
exec python3 "$ROOT/scripts/validate_iso.py" "$1" --report "${2:-$1.validation.json}"
