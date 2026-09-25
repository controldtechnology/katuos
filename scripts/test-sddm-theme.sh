#!/usr/bin/env bash
# Run the actual Katu greeter with Debian Trixie's Qt 6 SDDM under Xvfb.
set -Eeuo pipefail
THEME=${1:?usage: test-sddm-theme.sh THEME-DIRECTORY}
GREETER=$(command -v sddm-greeter-qt6 || command -v sddm-greeter)
command -v xvfb-run >/dev/null
LOG=$(mktemp)
trap 'rm -f "$LOG"' EXIT
set +e
timeout --foreground 15s xvfb-run -a env QT_QUICK_BACKEND=software \
    "$GREETER" --test-mode --theme "$THEME" >"$LOG" 2>&1
status=$?
set -e
cat "$LOG"
if grep -Eiq 'Fallback to embedded theme|cannot be loaded due to the errors|QQmlComponent: Component is not ready|Main.qml:.*(TypeError|ReferenceError)' "$LOG"; then
    echo 'SDDM_THEME: FAIL — greeter fell back or the Katu QML raised an error' >&2
    exit 1
fi
if [[ $status -ne 0 && $status -ne 124 ]]; then
    echo "SDDM_THEME: FAIL — greeter exited with status $status" >&2
    exit "$status"
fi
grep -Eq 'Loading theme configuration|Loading file:.*Main.qml|Greeter session started' "$LOG" || {
    echo 'SDDM_THEME: FAIL — no evidence that the greeter loaded the requested theme' >&2
    exit 1
}
echo 'SDDM_THEME: PASS — Qt 6 greeter loaded the Katu theme without fallback'
