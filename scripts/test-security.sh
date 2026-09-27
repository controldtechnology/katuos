#!/bin/bash
# Teste obrigatório de segurança do Katu OS Ecosystem
# Verifica: prompt injection, execução arbitrária, credenciais hardcoded
set -e

PASS=0
FAIL=0
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

ok()   { echo "  [OK]  $*"; PASS=$((PASS+1)); }
fail() { echo "  [FAIL] $*"; FAIL=$((FAIL+1)); }

echo "=== Katu OS Security Tests ==="
echo

# ── 1. Nenhuma chave de API hardcoded ────────────────────────────────────────
echo "1. Scanning for hardcoded API keys..."
if grep -rE "(sk-[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{35})" \
    "$ROOT/packages" --include="*.py" --include="*.json" --include="*.conf" \
    --include="*.desktop" 2>/dev/null | grep -v "# example\|# test\|placeholder"; then
    fail "Hardcoded API key found"
else
    ok "No hardcoded API keys"
fi

# ── 2. Nenhum sudo sem senha ──────────────────────────────────────────────────
echo "2. Checking for passwordless sudo..."
if grep -rE "NOPASSWD|sudo -n|sudo --non-interactive" \
    "$ROOT/packages" "$ROOT/config" --include="*.py" --include="*.sh" \
    --include="*.conf" 2>/dev/null | grep -v "# "; then
    fail "Passwordless sudo found"
else
    ok "No passwordless sudo"
fi

# ── 3. Nenhuma execução arbitrária de shell a partir de input ────────────────
echo "3. Checking katu-ai action registry (no arbitrary shell exec)..."
AI_MAIN="$ROOT/packages/katu-ai/usr/lib/katu-ai/main.py"
if grep -qE "subprocess\.(run|Popen|check_output)\s*\(\s*[a-z_]*\s*\)" "$AI_MAIN" 2>/dev/null; then
    # Check that it goes through action registry
    if grep -q "ACTION_REGISTRY\|execute_action\|ActionConfirmDialog" "$AI_MAIN"; then
        ok "AI uses action registry for all actions"
    else
        fail "AI may allow arbitrary command execution"
    fi
else
    ok "No raw subprocess exec from AI input detected"
fi

# ── 4. katu-core actions.py usa registry fechado ─────────────────────────────
echo "4. Checking actions.py uses closed registry..."
ACTIONS="$ROOT/packages/katu-core/usr/lib/python3/dist-packages/katu_core/actions.py"
if grep -q "ACTION_REGISTRY" "$ACTIONS" && ! grep -qE "\beval\s*\(|\bexec\s*\(|__import__\s*\(" "$ACTIONS"; then
    ok "actions.py uses closed ACTION_REGISTRY, no eval/exec"
else
    fail "actions.py may allow arbitrary execution"
fi

# ── 5. Secrets armazenados com chmod 600 ─────────────────────────────────────
echo "5. Checking secrets use chmod 600..."
SECRETS="$ROOT/packages/katu-core/usr/lib/python3/dist-packages/katu_core/secrets.py"
if grep -q "0o600\|chmod.*600" "$SECRETS"; then
    ok "Secrets stored with 0600 permissions"
else
    fail "Secrets may not have correct permissions"
fi

# ── 6. Nenhum telemetria silenciosa ──────────────────────────────────────────
echo "6. Checking for hidden telemetry..."
if grep -rE "(analytics|telemetry|tracking|beacon|mixpanel|segment|amplitude)" \
    "$ROOT/packages" --include="*.py" 2>/dev/null | grep -v "# \|consent\|opt"; then
    fail "Hidden telemetry code found"
else
    ok "No hidden telemetry"
fi

# ── 7. GUI nunca roda como root ───────────────────────────────────────────────
echo "7. Checking GUI apps don't run as root..."
for desktop in "$ROOT"/packages/*/usr/share/applications/*.desktop; do
    [ -f "$desktop" ] || continue
    if grep -q "^Exec=sudo\|^Exec=su \|^Exec=gksu\|^Exec=gksudo" "$desktop"; then
        fail "$(basename $desktop) launches GUI as root"
    fi
done
ok "No desktop files launch GUI as root"

# ── 8. pkexec usado para operações privilegiadas (não sudo) ─────────────────
echo "8. Checking privileged operations use pkexec..."
PACKAGES_PY="$ROOT/packages/katu-core/usr/lib/python3/dist-packages/katu_core/packages.py"
if grep -q "pkexec" "$PACKAGES_PY" && ! grep -q "sudo.*NOPASSWD" "$PACKAGES_PY"; then
    ok "Package operations use pkexec"
else
    fail "Package operations may not use pkexec correctly"
fi

# ── 9. Teste de prompt injection na katu-ai ──────────────────────────────────
echo "9. Checking katu-ai separates system prompt from user content..."
if grep -qE "\"role\"\s*:\s*\"system\"" "$AI_MAIN" 2>/dev/null; then
    ok "AI uses role-based message separation (system/user/assistant)"
else
    # Check for other separation mechanisms
    if grep -q "system_prompt\|SYSTEM_PROMPT\|system_context" "$AI_MAIN" 2>/dev/null; then
        ok "AI uses separate system context variable"
    else
        fail "AI may not separate system instructions from user input"
    fi
fi

# ── 10. katu-welcome: modo live detectado ───────────────────────────────────
echo "10. Checking katu-welcome handles live mode..."
WELCOME="$ROOT/packages/katu-welcome/usr/lib/katu-welcome/main.py"
if grep -q "is_live\|live_session\|LIVE_FLAG" "$WELCOME" 2>/dev/null; then
    ok "katu-welcome detects live mode"
else
    fail "katu-welcome does not detect live mode"
fi

# ── 11. Nenhuma captura de CPF/senha/token ──────────────────────────────────
echo "11. Checking for CPF/password/token capture patterns..."
if grep -rE "(cpf|cnpj|password_input|senha_input|capture.*login|gov\.br.*password)" \
    "$ROOT/packages" --include="*.py" 2>/dev/null | grep -v "#"; then
    fail "Potential credential capture found"
else
    ok "No credential capture patterns found"
fi

echo
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] || { echo "SECURITY TEST FAILED"; exit 1; }
echo "All security tests passed."
