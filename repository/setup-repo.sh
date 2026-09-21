#!/bin/bash
# Gerar repositório APT local do Katu OS
# Executar a partir da raiz do projeto: bash repository/setup-repo.sh

set -Eeuo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$REPO_DIR")"
POOL_DIR="${REPO_DIR}/pool/main"
DISTS_DIR="${REPO_DIR}/dists/katu/main/binary-amd64"

echo ">>> Katu OS — Gerando repositório APT local..."

# Passo 1: Compilar pacotes
echo ">>> Compilando pacotes .deb..."
for pkg in katu-release katu-branding katu-default-settings katu-welcome; do
    PKG_DIR="${PROJECT_DIR}/packages/${pkg}"
    DEB_FILE="${REPO_DIR}/pool/main/${pkg}_1.0_all.deb"
    echo "  → Compilando ${pkg}..."
    dpkg-deb --build --root-owner-group "${PKG_DIR}" "${DEB_FILE}"
done

# Passo 2: Gerar índice Packages
echo ">>> Gerando índice Packages..."
mkdir -p "${DISTS_DIR}"
cd "${REPO_DIR}"
dpkg-scanpackages --multiversion pool/main > "${DISTS_DIR}/Packages"
gzip -k -f "${DISTS_DIR}/Packages"

# Passo 3: Gerar Release
echo ">>> Gerando Release..."
cat > "${REPO_DIR}/dists/katu/Release" << EOF
Origin: Katu OS
Label: Katu OS
Suite: katu
Codename: katu
Version: 1.0
Architectures: amd64 all
Components: main
Description: Katu OS official package repository
Date: $(date -Ru)
EOF

# Calcular checksums
cd "${REPO_DIR}/dists/katu"
echo "MD5Sum:" >> Release
for f in main/binary-amd64/Packages main/binary-amd64/Packages.gz; do
    printf " %s %s %s\n" "$(md5sum ${f} | cut -d' ' -f1)" "$(wc -c < ${f})" "${f}" >> Release
done
echo "SHA256:" >> Release
for f in main/binary-amd64/Packages main/binary-amd64/Packages.gz; do
    printf " %s %s %s\n" "$(sha256sum ${f} | cut -d' ' -f1)" "$(wc -c < ${f})" "${f}" >> Release
done

echo ""
echo "✓ Repositório gerado em: ${REPO_DIR}"
echo ""
echo "Para usar:"
echo "  echo \"deb [trusted=yes] file://${REPO_DIR} katu main\" \\"
echo "    | sudo tee /etc/apt/sources.list.d/katu-local.list"
echo "  sudo apt update"
