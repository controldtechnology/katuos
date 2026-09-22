#!/bin/bash
# Katu OS — build.sh
# Script principal de build da ISO

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
BUILD_DIR="${PROJECT_ROOT}/build"
OUTPUT_DIR="${PROJECT_ROOT}/output"
LOGS_DIR="${PROJECT_ROOT}/logs"

# Importar configurações
source "${PROJECT_ROOT}/config/live-build.conf"

# Timestamp
BUILD_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="${LOGS_DIR}/build-${BUILD_TIMESTAMP}.log"

# Versão
KATU_VERSION=$(cat "${PROJECT_ROOT}/VERSION" | tr -d '[:space:]')
ISO_NAME="katu-os-${KATU_VERSION}-amd64.iso"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC}  $*" | tee -a "${LOG_FILE}"; }
log_ok()      { echo -e "${GREEN}[OK]${NC}    $*" | tee -a "${LOG_FILE}"; }
log_warn()    { echo -e "${YELLOW}[AVISO]${NC} $*" | tee -a "${LOG_FILE}"; }
log_error()   { echo -e "${RED}[ERRO]${NC}  $*" | tee -a "${LOG_FILE}" >&2; }
log_step()    { echo -e "${CYAN}[ETAPA]${NC} $*" | tee -a "${LOG_FILE}"; }

# Verificações iniciais
if [[ "$(uname -s)" != "Linux" ]]; then
    echo "ERRO: Este script deve ser executado no Linux." >&2
    exit 1
fi

if [[ $EUID -ne 0 ]]; then
    echo "ERRO: Execute como root ou com sudo." >&2
    exec sudo bash "$0" "$@"
fi

if ! command -v lb &>/dev/null; then
    echo "ERRO: live-build não encontrado. Execute primeiro: bash scripts/setup-build-env.sh" >&2
    exit 1
fi

# Criar diretórios
mkdir -p "${BUILD_DIR}" "${OUTPUT_DIR}" "${LOGS_DIR}"

echo "======================================================" | tee "${LOG_FILE}"
echo "  KATU OS BUILD SYSTEM" | tee -a "${LOG_FILE}"
echo "  Versão: ${KATU_VERSION}" | tee -a "${LOG_FILE}"
echo "  Data: $(date)" | tee -a "${LOG_FILE}"
echo "  Log: ${LOG_FILE}" | tee -a "${LOG_FILE}"
echo "======================================================" | tee -a "${LOG_FILE}"

# === ETAPA 1: Construir pacotes próprios ===
log_step "1/6 — Construindo pacotes Katu..."

PACKAGES_DIR="${PROJECT_ROOT}/packages"
PACKAGES_OUTPUT="${BUILD_DIR}/packages"
mkdir -p "${PACKAGES_OUTPUT}"

for pkg_dir in "${PACKAGES_DIR}"/*/; do
    pkg_name=$(basename "${pkg_dir}")
    log_info "  Construindo: ${pkg_name}"

    # Garantir permissões nos scripts DEBIAN
    find "${pkg_dir}/DEBIAN" -name "postinst" -o -name "preinst" \
         -o -name "postrm" -o -name "prerm" 2>/dev/null | \
        xargs -r chmod 755

    # Construir .deb
    dpkg-deb --build "${pkg_dir}" "${PACKAGES_OUTPUT}/${pkg_name}.deb" 2>>"${LOG_FILE}" || {
        log_warn "  Falhou ao construir ${pkg_name} — continuando"
    }

    if [[ -f "${PACKAGES_OUTPUT}/${pkg_name}.deb" ]]; then
        log_ok "  Construído: ${pkg_name}.deb"
    fi
done

# Criar repositório local
if ls "${PACKAGES_OUTPUT}"/*.deb &>/dev/null; then
    log_info "  Criando repositório local de pacotes..."
    cd "${PACKAGES_OUTPUT}"
    dpkg-scanpackages . /dev/null > Packages 2>>"${LOG_FILE}"
    gzip -k Packages
    cd - > /dev/null
    log_ok "  Repositório local criado em ${PACKAGES_OUTPUT}"
fi

# === ETAPA 2: Configurar live-build ===
log_step "2/6 — Configurando live-build..."

cd "${BUILD_DIR}"

# Copiar configurações
if [[ -d "${PROJECT_ROOT}/config" ]]; then
    rsync -av "${PROJECT_ROOT}/config/" "${BUILD_DIR}/config/" >>"${LOG_FILE}" 2>&1
fi

# Copiar assets para includes.chroot
log_info "  Copiando assets..."

# SDDM theme
if [[ -d "${PROJECT_ROOT}/sddm" ]]; then
    mkdir -p "${BUILD_DIR}/config/includes.chroot/usr/share/sddm/themes"
    rsync -av "${PROJECT_ROOT}/sddm/" \
        "${BUILD_DIR}/config/includes.chroot/usr/share/sddm/themes/" \
        >>"${LOG_FILE}" 2>&1
fi

# Plymouth theme
if [[ -d "${PROJECT_ROOT}/plymouth" ]]; then
    mkdir -p "${BUILD_DIR}/config/includes.chroot/usr/share/plymouth/themes"
    rsync -av "${PROJECT_ROOT}/plymouth/" \
        "${BUILD_DIR}/config/includes.chroot/usr/share/plymouth/themes/" \
        >>"${LOG_FILE}" 2>&1
fi

# GRUB theme
if [[ -d "${PROJECT_ROOT}/grub" ]]; then
    mkdir -p "${BUILD_DIR}/config/includes.binary/boot/grub/themes"
    rsync -av "${PROJECT_ROOT}/grub/" \
        "${BUILD_DIR}/config/includes.binary/boot/grub/themes/" \
        >>"${LOG_FILE}" 2>&1
fi

# Plasma themes
if [[ -d "${PROJECT_ROOT}/plasma" ]]; then
    mkdir -p "${BUILD_DIR}/config/includes.chroot/usr/share"
    rsync -av "${PROJECT_ROOT}/plasma/" \
        "${BUILD_DIR}/config/includes.chroot/usr/share/plasma/" \
        >>"${LOG_FILE}" 2>&1
fi

# Calamares
if [[ -d "${PROJECT_ROOT}/installer/calamares" ]]; then
    mkdir -p "${BUILD_DIR}/config/includes.chroot/etc/calamares"
    rsync -av "${PROJECT_ROOT}/installer/calamares/" \
        "${BUILD_DIR}/config/includes.chroot/etc/calamares/" \
        >>"${LOG_FILE}" 2>&1
fi

# Repositório local de pacotes Katu
mkdir -p "${BUILD_DIR}/config/archives"
cat > "${BUILD_DIR}/config/archives/katu-local.list.chroot" << EOF
deb [trusted=yes] file://${PACKAGES_OUTPUT} ./
EOF

# Configurar live-build
lb config \
    --distribution "${LB_DISTRIBUTION}" \
    --architecture "${LB_ARCHITECTURE}" \
    --mirror-bootstrap "${LB_MIRROR_BOOTSTRAP}" \
    --mirror-chroot "${LB_MIRROR_CHROOT}" \
    --mirror-chroot-security "${LB_MIRROR_CHROOT_SECURITY}" \
    --archive-areas "${LB_ARCHIVE_AREAS}" \
    --bootloaders "${LB_BOOTLOADERS}" \
    --debian-installer none \
    --memtest none \
    --iso-application "${LB_ISO_APPLICATION}" \
    --iso-preparer "${LB_ISO_PREPARER}" \
    --iso-publisher "${LB_ISO_PUBLISHER}" \
    --iso-volume "${LB_ISO_VOLUME}" \
    --image-type iso-hybrid \
    --binary-filesystem fat32 \
    --hostname "${LB_HOSTNAME}" \
    --username "${LB_USERNAME}" \
    --compression xz \
    --verbose \
    2>>"${LOG_FILE}"

log_ok "live-build configurado."

# === ETAPA 3: Executar build ===
log_step "3/6 — Executando lb build (isso leva tempo)..."
log_info "  Acompanhe o progresso em: ${LOG_FILE}"

SECONDS=0
lb build 2>&1 | tee -a "${LOG_FILE}"
BUILD_EXIT=${PIPESTATUS[0]}
BUILD_DURATION=$SECONDS

if [[ $BUILD_EXIT -ne 0 ]]; then
    log_error "lb build falhou com código ${BUILD_EXIT}"
    log_error "Verifique: ${LOG_FILE}"
    exit $BUILD_EXIT
fi

log_ok "Build concluído em $(( BUILD_DURATION / 60 ))m$(( BUILD_DURATION % 60 ))s"

# === ETAPA 4: Localizar e mover ISO ===
log_step "4/6 — Localizando ISO gerada..."

ISO_GENERATED=""
for candidate in \
    "${BUILD_DIR}/live-image-amd64.hybrid.iso" \
    "${BUILD_DIR}/katu-os.iso" \
    "${BUILD_DIR}"/*.iso; do
    if [[ -f "$candidate" ]]; then
        ISO_GENERATED="$candidate"
        break
    fi
done

if [[ -z "$ISO_GENERATED" ]]; then
    log_error "ISO não encontrada após o build!"
    exit 1
fi

log_ok "ISO encontrada: ${ISO_GENERATED}"
ISO_SIZE=$(du -sh "${ISO_GENERATED}" | cut -f1)
log_info "Tamanho: ${ISO_SIZE}"

# === ETAPA 5: Mover e renomear ===
log_step "5/6 — Movendo ISO para output/..."

ISO_FINAL="${OUTPUT_DIR}/${ISO_NAME}"
mv "${ISO_GENERATED}" "${ISO_FINAL}"
log_ok "ISO: ${ISO_FINAL}"

# === ETAPA 6: Checksum e info ===
log_step "6/6 — Gerando checksum e build-info..."

bash "${SCRIPT_DIR}/checksum.sh" "${ISO_FINAL}"

# Validar conteúdo da ISO
log_step "Validando conteúdo da ISO..."
bash "${SCRIPT_DIR}/validate-iso.sh" "${ISO_FINAL}" || {
    log_error "Validação da ISO falhou! A ISO pode ter problemas."
    log_error "Verifique o conteúdo antes de distribuir."
    exit 1
}

# build-info.txt
cat > "${OUTPUT_DIR}/build-info.txt" << EOF
KATU_ISO=${ISO_NAME}
KATU_VERSION=${KATU_VERSION}
KATU_BUILD_DATE=$(date +%Y-%m-%d)
KATU_BUILD_TIME=$(date +%H:%M:%S)
KATU_BUILD_DURATION=${BUILD_DURATION}s
KATU_BASE=Debian ${LB_DISTRIBUTION}
KATU_ARCH=${LB_ARCHITECTURE}
KATU_ISO_SIZE=${ISO_SIZE}
BUILD_HOST=$(hostname)
BUILD_KERNEL=$(uname -r)
EOF

log_ok "build-info.txt gerado."

# Resumo final
echo
echo "======================================================"
echo -e "  ${GREEN}BUILD CONCLUÍDO COM SUCESSO${NC}"
echo "======================================================"
echo "  ISO:      ${ISO_FINAL}"
echo "  SHA256:   ${ISO_FINAL}.sha256"
echo "  Info:     ${OUTPUT_DIR}/build-info.txt"
echo "  Log:      ${LOG_FILE}"
echo "  Tempo:    $(( BUILD_DURATION / 60 ))m$(( BUILD_DURATION % 60 ))s"
echo "======================================================"
echo
log_info "Para testar: bash scripts/validate.sh"
echo
