#!/bin/bash
# Katu OS — setup-build-env.sh
# Prepara o ambiente de build no Debian/Ubuntu
# Execute como root ou com sudo

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()    { echo -e "${YELLOW}[AVISO]${NC} $*"; }
log_error()   { echo -e "${RED}[ERRO]${NC}  $*" >&2; }

# --- Verificações iniciais ---

log_info "=== Katu OS — Configuração do Ambiente de Build ==="
log_info "Projeto: ${PROJECT_ROOT}"

# Verificar se está no Linux
if [[ "$(uname -s)" != "Linux" ]]; then
    log_error "Este script deve ser executado no Linux."
    log_error "No Windows, habilite WSL2 e execute nele."
    exit 1
fi

# Verificar distribuição
if ! command -v apt-get &>/dev/null; then
    log_error "APT não encontrado. Este script requer Debian ou Ubuntu."
    exit 1
fi

# Verificar privileges
if [[ $EUID -ne 0 ]]; then
    log_warn "Este script deve ser executado como root."
    log_info "Tentando com sudo..."
    exec sudo bash "$0" "$@"
fi

log_ok "Ambiente Linux detectado."

# --- Atualizar repositórios ---
log_info "Atualizando lista de pacotes..."
apt-get update -qq
log_ok "Lista de pacotes atualizada."

# --- Instalar dependências live-build ---
log_info "Instalando dependências do live-build..."

DEPS=(
    live-build
    debootstrap
    squashfs-tools
    xorriso
    isolinux
    syslinux
    syslinux-common
    grub-pc-bin
    grub-efi-amd64-bin
    grub-efi-amd64-signed
    mtools
    dosfstools
    dpkg-dev
    fakeroot
    devscripts
    debhelper
    dh-python
    python3
    python3-pyqt5
    git
    wget
    curl
    ca-certificates
    rsync
    genisoimage
    ovmf
    qemu-utils
)

for dep in "${DEPS[@]}"; do
    if dpkg -l "$dep" &>/dev/null; then
        log_ok "  Já instalado: $dep"
    else
        log_info "  Instalando: $dep"
        apt-get install -y --no-install-recommends "$dep" 2>/dev/null || \
            log_warn "  Não encontrado (opcional): $dep"
    fi
done

# --- Verificar live-build ---
if ! command -v lb &>/dev/null; then
    log_error "live-build não foi instalado corretamente."
    exit 1
fi

log_ok "live-build disponível: $(lb --version)"

# --- Preparar diretórios ---
log_info "Preparando diretórios do projeto..."

mkdir -p "${PROJECT_ROOT}/build"
mkdir -p "${PROJECT_ROOT}/output"
mkdir -p "${PROJECT_ROOT}/logs"
mkdir -p "${PROJECT_ROOT}/cache"

log_ok "Diretórios criados."

# --- Verificar ISO base ---
ISO_BASE="${PROJECT_ROOT}/base/debian-live-13.7.0-amd64-kde.iso"
if [[ -f "${ISO_BASE}" ]]; then
    log_ok "ISO Debian encontrada: ${ISO_BASE}"
    ISO_SIZE=$(du -sh "${ISO_BASE}" | cut -f1)
    log_info "Tamanho: ${ISO_SIZE}"
else
    log_warn "ISO Debian não encontrada em ${ISO_BASE}"
    log_warn "O build usará debootstrap para baixar o sistema base."
fi

# --- Relatório final ---
echo
log_ok "=== Ambiente de build pronto ==="
log_info "Para iniciar o build:"
log_info "  cd ${PROJECT_ROOT}"
log_info "  bash scripts/build.sh"
echo
