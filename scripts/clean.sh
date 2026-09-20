#!/bin/bash
# Katu OS — clean.sh
# Limpa artefatos de build sem destruir código/configuração

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
BUILD_DIR="${PROJECT_ROOT}/build"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[AVISO]${NC} $*"; }
log_error() { echo -e "${RED}[ERRO]${NC}  $*" >&2; }

echo "=== Katu OS — Limpeza ==="

# Modo: full ou partial
MODE="${1:-partial}"

if [[ "$MODE" == "full" ]]; then
    log_warn "Limpeza COMPLETA solicitada."
    log_warn "Isso removerá build/, cache/ e pacotes .deb gerados."
    read -r -p "Confirmar limpeza completa? [s/N] " resp
    if [[ "$resp" != "s" && "$resp" != "S" ]]; then
        echo "Limpeza cancelada."
        exit 0
    fi
fi

# Limpeza live-build
if [[ -d "${BUILD_DIR}" ]]; then
    if [[ "$MODE" == "full" ]]; then
        if command -v lb &>/dev/null; then
            cd "${BUILD_DIR}" && lb clean --all 2>/dev/null || true && cd - > /dev/null
        fi
        rm -rf "${BUILD_DIR}"
        log_ok "Diretório build/ removido."
    else
        if command -v lb &>/dev/null; then
            cd "${BUILD_DIR}" && lb clean 2>/dev/null || true && cd - > /dev/null
            log_ok "Artefatos live-build limpos (cache preservado)."
        fi
    fi
fi

# Limpar pacotes .deb temporários
if [[ "$MODE" == "full" ]]; then
    find "${PROJECT_ROOT}/packages" -name "*.deb" -delete 2>/dev/null || true
    log_ok "Pacotes .deb temporários removidos."
fi

# Limpar logs antigos (manter últimos 5)
if [[ -d "${PROJECT_ROOT}/logs" ]]; then
    LOGS_COUNT=$(find "${PROJECT_ROOT}/logs" -name "build-*.log" | wc -l)
    if [[ $LOGS_COUNT -gt 5 ]]; then
        find "${PROJECT_ROOT}/logs" -name "build-*.log" | \
            sort | head -n $(( LOGS_COUNT - 5 )) | xargs rm -f
        log_ok "Logs antigos removidos (mantidos: 5)."
    fi
fi

log_ok "Limpeza concluída."
echo
echo "Uso: $0 [partial|full]"
echo "  partial (padrão): limpa artefatos, preserva cache"
echo "  full: limpa tudo inclusive cache e pacotes"
