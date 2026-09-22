#!/bin/bash
# Katu OS — validate-iso.sh
# Valida o conteúdo da ISO gerada antes de marcá-la como release.
# Uso: bash scripts/validate-iso.sh [caminho/para/katu-os.iso]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERROS=0
AVISOS=0
MOUNT_DIR=""

ok()   { echo -e "  ${GREEN}✓${NC} $*"; }
fail() { echo -e "  ${RED}✗ ERRO:${NC} $*" >&2; (( ERROS++ )) || true; }
warn() { echo -e "  ${YELLOW}! AVISO:${NC} $*"; (( AVISOS++ )) || true; }
info() { echo -e "  ${BLUE}·${NC} $*"; }

cleanup() {
    if [[ -n "${MOUNT_DIR}" && -d "${MOUNT_DIR}" ]]; then
        sudo umount "${MOUNT_DIR}" 2>/dev/null || true
        rmdir "${MOUNT_DIR}" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Localizar ISO
ISO_PATH="${1:-}"
if [[ -z "${ISO_PATH}" ]]; then
    ISO_PATH=$(find "${PROJECT_ROOT}/output" -name "*.iso" | sort | tail -1)
fi

echo "=========================================="
echo "  Katu OS — Validação da ISO"
echo "=========================================="
echo

if [[ -z "${ISO_PATH}" || ! -f "${ISO_PATH}" ]]; then
    echo -e "${RED}ERRO: ISO não encontrada.${NC}"
    echo "  Use: bash scripts/validate-iso.sh caminho/para/katu.iso"
    echo "  Ou gere a ISO primeiro: bash scripts/build.sh"
    exit 1
fi

info "ISO: ${ISO_PATH}"
ISO_SIZE_BYTES=$(stat -c%s "${ISO_PATH}")
ISO_SIZE_MB=$(( ISO_SIZE_BYTES / 1024 / 1024 ))
info "Tamanho: ${ISO_SIZE_MB} MB"
echo

# === 1. Verificações básicas da ISO ===
echo "1. Verificações básicas"

if [[ ${ISO_SIZE_BYTES} -lt 500000000 ]]; then
    fail "ISO muito pequena (${ISO_SIZE_MB} MB < 500 MB) — build incompleto?"
elif [[ ${ISO_SIZE_BYTES} -gt 8000000000 ]]; then
    warn "ISO muito grande (${ISO_SIZE_MB} MB > 8 GB)"
else
    ok "Tamanho razoável: ${ISO_SIZE_MB} MB"
fi

if file "${ISO_PATH}" | grep -q "ISO 9660\|x86 boot"; then
    ok "Formato ISO reconhecido"
else
    fail "Não parece um arquivo ISO válido: $(file "${ISO_PATH}")"
fi

echo

# === 2. Montar a ISO ===
echo "2. Montando ISO para inspeção"

if ! command -v fuseiso &>/dev/null && ! command -v isoinfo &>/dev/null; then
    warn "fuseiso/isoinfo não instalados — usando isoinfo para listar conteúdo"
    USE_MOUNT=false
else
    USE_MOUNT=true
fi

if command -v isoinfo &>/dev/null; then
    # Listar arquivos sem montar
    ISO_LISTING=$(isoinfo -l -i "${ISO_PATH}" 2>/dev/null || true)

    check_iso_file() {
        local path="$1"
        local desc="$2"
        local upper_path
        upper_path=$(echo "$path" | tr '[:lower:]' '[:upper:]' | sed 's|/|/|g')
        # isoinfo lista em maiúsculas com extensão .;1
        if echo "${ISO_LISTING}" | grep -qi "$(basename "${upper_path}")"; then
            ok "${desc} encontrado: ${path}"
            return 0
        else
            fail "${desc} NÃO encontrado: ${path}"
            return 1
        fi
    }

    echo "3. Conteúdo crítico (via isoinfo)"
    check_iso_file "/live/vmlinuz"          "Kernel"
    check_iso_file "/live/initrd.img"       "Initrd"
    check_iso_file "/live/filesystem.squashfs" "Filesystem squashfs"
    check_iso_file "/boot/grub/grub.cfg"    "GRUB config (BIOS)"

    # Verificar estrutura EFI
    if echo "${ISO_LISTING}" | grep -qi "EFI\|grubx64.efi"; then
        ok "Estrutura EFI presente"
    else
        warn "Estrutura EFI não detectada (pode estar correta mesmo assim)"
    fi

elif [[ "${USE_MOUNT}" == true ]]; then
    MOUNT_DIR=$(mktemp -d /tmp/katu-iso-XXXXXX)
    if sudo mount -o loop,ro "${ISO_PATH}" "${MOUNT_DIR}" 2>/dev/null; then
        ok "ISO montada em ${MOUNT_DIR}"
        echo

        echo "3. Conteúdo crítico"

        check_file() {
            local path="${MOUNT_DIR}${1}"
            local desc="$2"
            local critical="${3:-true}"
            if [[ -f "${path}" ]]; then
                local size
                size=$(du -sh "${path}" | cut -f1)
                ok "${desc}: ${1} (${size})"
                return 0
            else
                if [[ "${critical}" == "true" ]]; then
                    fail "${desc} NÃO encontrado: ${1}"
                else
                    warn "${desc} não encontrado: ${1}"
                fi
                return 1
            fi
        }

        check_file "/live/vmlinuz"              "Kernel (sem versão)"
        check_file "/live/initrd.img"           "Initrd (sem versão)"
        check_file "/live/filesystem.squashfs"  "Filesystem squashfs"
        check_file "/boot/grub/grub.cfg"        "GRUB config (BIOS)"
        check_file "/boot/grub/loopback.cfg"    "loopback.cfg (Ventoy)" false

        # Verificar squashfs não está vazio
        SQUASHFS="${MOUNT_DIR}/live/filesystem.squashfs"
        if [[ -f "${SQUASHFS}" ]]; then
            SQ_SIZE=$(stat -c%s "${SQUASHFS}")
            if [[ ${SQ_SIZE} -lt 100000000 ]]; then
                fail "filesystem.squashfs muito pequeno ($(du -sh "${SQUASHFS}" | cut -f1)) — build falhou?"
            else
                ok "squashfs tamanho OK: $(du -sh "${SQUASHFS}" | cut -f1)"
            fi
        fi

        echo

        echo "4. Consistência GRUB ↔ arquivos"

        GRUB_CFG="${MOUNT_DIR}/boot/grub/grub.cfg"
        if [[ -f "${GRUB_CFG}" ]]; then
            # Verificar que grub.cfg NÃO referencia wildcards literais
            if grep -q 'vmlinuz-\*\|initrd.img-\*' "${GRUB_CFG}" 2>/dev/null; then
                fail "grub.cfg contém wildcards literais (vmlinuz-* ou initrd.img-*) — ERRO DE BUILD"
            else
                ok "grub.cfg sem wildcards problemáticos"
            fi

            # Verificar que cada 'linux' e 'initrd' no grub.cfg aponta para arquivo existente
            GRUB_KERNEL_PATHS=$(grep -E '^\s*linux\s+' "${GRUB_CFG}" | awk '{print $2}' | sort -u)
            GRUB_INITRD_PATHS=$(grep -E '^\s*initrd\s+' "${GRUB_CFG}" | awk '{print $2}' | sort -u)

            PATHS_OK=true
            for kpath in ${GRUB_KERNEL_PATHS}; do
                if [[ -f "${MOUNT_DIR}${kpath}" ]]; then
                    ok "Kernel referenciado pelo GRUB existe: ${kpath}"
                else
                    fail "GRUB referencia kernel INEXISTENTE na ISO: ${kpath}"
                    PATHS_OK=false
                fi
            done

            for ipath in ${GRUB_INITRD_PATHS}; do
                if [[ -f "${MOUNT_DIR}${ipath}" ]]; then
                    ok "Initrd referenciado pelo GRUB existe: ${ipath}"
                else
                    fail "GRUB referencia initrd INEXISTENTE na ISO: ${ipath}"
                    PATHS_OK=false
                fi
            done

            if [[ "${PATHS_OK}" == true && -z "$(echo "${GRUB_KERNEL_PATHS}")" ]]; then
                warn "Nenhum path de kernel encontrado no grub.cfg — verificar manualmente"
            fi
        fi

        echo

        echo "5. Estrutura EFI"
        if [[ -d "${MOUNT_DIR}/EFI" ]]; then
            ok "Diretório /EFI presente"
            if find "${MOUNT_DIR}/EFI" -name "*.efi" | grep -q .; then
                ok "Arquivos .efi encontrados em /EFI/"
            else
                warn "Nenhum arquivo .efi em /EFI/"
            fi
        else
            warn "/EFI/ não encontrado — boot UEFI pode não funcionar"
        fi

        if [[ -d "${MOUNT_DIR}/boot/efi" ]] || find "${MOUNT_DIR}" -name "grubx64.efi" -o -name "grub.efi" 2>/dev/null | grep -q .; then
            ok "GRUB EFI presente"
        else
            warn "GRUB EFI não detectado na estrutura da ISO"
        fi

        echo

        echo "6. Branding Katu OS"
        for asset in \
            "/boot/grub/themes/katu/theme.txt" \
            "/etc/os-release" ; do
            if [[ -f "${MOUNT_DIR}${asset}" ]]; then
                ok "Asset: ${asset}"
            else
                warn "Asset não encontrado: ${asset}"
            fi
        done

        # Verificar squashfs internamente (conteúdo do sistema instalado)
        if command -v unsquashfs &>/dev/null; then
            SQUASHFS_TMP=$(mktemp -d /tmp/katu-sq-XXXXXX)
            trap "cleanup; rm -rf '${SQUASHFS_TMP}'" EXIT
            if sudo unsquashfs -l "${MOUNT_DIR}/live/filesystem.squashfs" \
                    2>/dev/null | grep -q "/usr/share/wallpapers/katu"; then
                ok "Wallpapers Katu no squashfs"
            else
                warn "Wallpapers Katu não encontrados no squashfs"
            fi
            rm -rf "${SQUASHFS_TMP}"
        fi

    else
        warn "Não foi possível montar a ISO (root necessário)"
    fi
fi

echo

# === Resumo ===
echo "=========================================="
if [[ ${ERROS} -eq 0 && ${AVISOS} -eq 0 ]]; then
    echo -e "${GREEN}✓ VALIDAÇÃO: PASSOU${NC}"
    echo -e "  ISO pronta para distribuição."
elif [[ ${ERROS} -eq 0 ]]; then
    echo -e "${YELLOW}! VALIDAÇÃO: AVISOS${NC}"
    echo -e "  ${AVISOS} aviso(s) — ISO pode funcionar mas revisar os avisos."
else
    echo -e "${RED}✗ VALIDAÇÃO: FALHOU${NC}"
    echo -e "  ${ERROS} erro(s) crítico(s) — ISO NÃO está pronta para distribuição."
    echo
    echo "  NÃO marque esta ISO como release."
fi
echo "=========================================="
echo

[[ ${ERROS} -eq 0 ]]
