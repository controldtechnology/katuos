#!/bin/bash
# Source checks first; --root also checks the completed chroot before ISO creation.
set -Eeuo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
for tool in python3 lb xorriso unsquashfs unmkinitramfs grub-script-check mcopy rsync dpkg-deb; do
    command -v "$tool" >/dev/null || { echo "Missing required tool: $tool" >&2; exit 1; }
done
python3 "$ROOT/scripts/validate-installer.py"
cmp "$ROOT/plasma/look-and-feel/org.katuos.desktop/contents/layouts/org.kde.plasma.desktop-layout.js" \
    "$ROOT/config/includes.chroot/usr/share/plasma/look-and-feel/org.katuos.desktop/contents/layouts/org.kde.plasma.desktop-layout.js"
cmp "$ROOT/sddm/katu/Main.qml" "$ROOT/config/includes.chroot/usr/share/sddm/themes/katu/Main.qml"
cmp "$ROOT/installer/calamares/branding/katu/stylesheet.qss" \
    "$ROOT/config/includes.chroot/etc/calamares/branding/katu/stylesheet.qss"
python3 - "$ROOT" "$@" <<'PY'
import sys, tempfile
from pathlib import Path
project = Path(sys.argv[1])
sys.path.insert(0, str(project / 'scripts'))
from boot_checks import grub_entries, require, rootfs_check, kernel_version, initrd_check, png_check
for directory in ['packages', 'installer', 'sddm', 'plymouth', 'grub', 'config/includes.chroot']:
    for asset in (project / directory).rglob('*.png'):
        png_check(asset)
for config in (project / 'config/bootloaders').rglob('grub.cfg'):
    grub_entries(config)
grub_entries(project / 'config/includes.binary/boot/grub/loopback.cfg')
if len(sys.argv) > 2:
    require(sys.argv[2] == '--root' and len(sys.argv) == 4, 'Usage: preflight-check.sh [--root CHROOT]')
    root = Path(sys.argv[3]).resolve()
    kernels = list((root / 'boot').glob('vmlinuz-*'))
    require(len(kernels) == 1, 'Expected exactly one kernel in clean chroot')
    version = kernel_version(kernels[0])
    config = rootfs_check(root, version)
    with tempfile.TemporaryDirectory(prefix='katu-preflight-') as temp:
        initrd_check(root / ('boot/initrd.img-' + version), version, Path(temp), config)
print('PREFLIGHT: PASS')
PY
if [[ ${1:-} == --root ]]; then
    python3 "$ROOT/scripts/validate-installer.py" --root "$2"
fi
