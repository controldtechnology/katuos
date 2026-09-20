#!/bin/bash
# Katu OS — validate.sh
# Valida estrutura do projeto, dependências e ISO

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERROS=0
AVISOS=0

ok()   { echo -e "  ${GREEN}✓${NC} $*"; }
fail() { echo -e "  ${RED}✗${NC} $*"; (( ERROS++ )); }
warn() { echo -e "  ${YELLOW}!${NC} $*"; (( AVISOS++ )); }
info() { echo -e "  ${BLUE}·${NC} $*"; }

echo "=== Katu OS — Validação do Projeto ==="
echo

# === 1. Estrutura de diretórios ===
echo "1. Estrutura de diretórios"
DIRS_REQUIRED=(
    "config/package-lists"
    "config/hooks/live"
    "config/bootloaders/grub-pc"
    "packages/katu-release"
    "packages/katu-branding"
    "packages/katu-default-settings"
    "packages/katu-welcome"
    "installer/calamares"
    "sddm/katu"
    "plymouth/katu"
    "grub/katu"
    "scripts"
    "docs"
    "output"
)

for d in "${DIRS_REQUIRED[@]}"; do
    if [[ -d "${PROJECT_ROOT}/${d}" ]]; then
        ok "${d}"
    else
        fail "${d} — AUSENTE"
    fi
done

echo

# === 2. Arquivos críticos ===
echo "2. Arquivos críticos"
FILES_REQUIRED=(
    "config/live-build.conf"
    "config/package-lists/kde.list.chroot"
    "config/package-lists/apps.list.chroot"
    "config/package-lists/katu.list.chroot"
    "config/bootloaders/grub-pc/grub.cfg"
    "packages/katu-release/DEBIAN/control"
    "packages/katu-release/etc/os-release"
    "packages/katu-welcome/DEBIAN/control"
    "packages/katu-welcome/usr/lib/katu-welcome/main.py"
    "installer/calamares/settings.conf"
    "installer/calamares/branding/katu/branding.desc"
    "sddm/katu/Main.qml"
    "sddm/katu/metadata.desktop"
    "plymouth/katu/katu.plymouth"
    "scripts/build.sh"
    "scripts/setup-build-env.sh"
    "README.md"
    "VERSION"
)

for f in "${FILES_REQUIRED[@]}"; do
    if [[ -f "${PROJECT_ROOT}/${f}" ]]; then
        ok "${f}"
    else
        fail "${f} — AUSENTE"
    fi
done

echo

# === 3. Assets visuais ===
echo "3. Assets visuais"
ASSETS=(
    "branding/logos"
    "wallpapers"
)

for a in "${ASSETS[@]}"; do
    if [[ -d "${PROJECT_ROOT}/${a}" ]]; then
        COUNT=$(find "${PROJECT_ROOT}/${a}" -type f | wc -l)
        if [[ $COUNT -gt 0 ]]; then
            ok "${a} (${COUNT} arquivo(s))"
        else
            warn "${a} — diretório vazio (assets pendentes)"
        fi
    else
        warn "${a} — ausente"
    fi
done

echo

# === 4. Dependências de build (Linux) ===
echo "4. Dependências de build"
TOOLS=( lb debootstrap xorriso squashfs-tools dpkg-dev fakeroot )

for tool in "${TOOLS[@]}"; do
    if command -v "${tool}" &>/dev/null; then
        ok "${tool} — $(${tool} --version 2>&1 | head -1 || echo 'disponível')"
    else
        warn "${tool} — não encontrado (instalar antes do build)"
    fi
done

echo

# === 5. ISO base ===
echo "5. ISO base Debian"
ISO_BASE="${PROJECT_ROOT}/base/debian-live-13.7.0-amd64-kde.iso"
if [[ -f "${ISO_BASE}" ]]; then
    ISO_SIZE=$(du -sh "${ISO_BASE}" | cut -f1)
    ok "ISO Debian: ${ISO_SIZE}"
else
    warn "ISO Debian não encontrada em base/"
    info "  O build usará debootstrap (download durante build)"
fi

echo

# === 6. Verificar output ===
echo "6. Output"
ISO_OUTPUT="${PROJECT_ROOT}/output"
ISO_COUNT=$(find "${ISO_OUTPUT}" -name "*.iso" | wc -l)
if [[ $ISO_COUNT -gt 0 ]]; then
    ok "ISO(s) em output/: ${ISO_COUNT}"
    find "${ISO_OUTPUT}" -name "*.iso" -exec ls -lh {} \;
else
    info "Nenhuma ISO gerada ainda (executar scripts/build.sh)"
fi

echo

# === Resumo ===
echo "======================================="
if [[ $ERROS -eq 0 && $AVISOS -eq 0 ]]; then
    echo -e "${GREEN}Validação: PASSOU${NC} — sem problemas"
elif [[ $ERROS -eq 0 ]]; then
    echo -e "${YELLOW}Validação: AVISOS${NC} — ${AVISOS} aviso(s), sem erros críticos"
else
    echo -e "${RED}Validação: FALHOU${NC} — ${ERROS} erro(s), ${AVISOS} aviso(s)"
fi
echo

[[ $ERROS -eq 0 ]]
