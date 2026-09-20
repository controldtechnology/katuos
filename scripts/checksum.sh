#!/bin/bash
# Katu OS — checksum.sh
# Gera checksums SHA256 para a ISO

set -Eeuo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

if [[ $# -eq 0 ]]; then
    echo "Uso: $0 <arquivo.iso>"
    exit 1
fi

ISO_FILE="$1"

if [[ ! -f "${ISO_FILE}" ]]; then
    echo -e "${RED}[ERRO]${NC} Arquivo não encontrado: ${ISO_FILE}" >&2
    exit 1
fi

echo -e "${GREEN}[INFO]${NC} Gerando SHA256 para: $(basename "${ISO_FILE}")"

sha256sum "${ISO_FILE}" > "${ISO_FILE}.sha256"

echo -e "${GREEN}[OK]${NC} Checksum: ${ISO_FILE}.sha256"
cat "${ISO_FILE}.sha256"
