#!/bin/bash
# One clean, isolated build. Older ISOs, logs and build trees remain evidence.
set -Eeuo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
[[ $EUID == 0 ]] || { echo 'Run as root' >&2; exit 1; }
source "$ROOT/config/live-build.conf"
VERSION=$(tr -d '[:space:]' < "$ROOT/VERSION")
COMMIT=$(git -C "$ROOT" rev-parse HEAD)
export SOURCE_DATE_EPOCH=$(git -C "$ROOT" show -s --format=%ct HEAD)
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
WORK="$ROOT/build/clean-$STAMP-${COMMIT:0:8}"
OUT="$ROOT/output/candidate-$STAMP-${COMMIT:0:8}"
[[ ! -e $WORK && ! -e $OUT ]]
mkdir -p "$WORK" "$OUT"
exec > >(tee "$OUT/build.log") 2>&1
trap 'echo "BUILD FAILED — no release approval" >&2' ERR
bash "$ROOT/scripts/preflight-check.sh"
python3 -m unittest discover -s "$ROOT/scripts/tests" -v
mkdir -p "$WORK/packages"
for package in "$ROOT"/packages/*; do
    find "$package/DEBIAN" -type f \( -name postinst -o -name preinst -o -name postrm -o -name prerm \) -exec chmod 755 {} +
    dpkg-deb --build --root-owner-group "$package" "$WORK/packages/$(basename "$package").deb"
done
(cd "$WORK/packages"; dpkg-scanpackages . /dev/null > Packages; gzip -k Packages)
rsync -a "$ROOT/config/" "$WORK/config/"
for asset in sddm plymouth grub plasma; do
    case "$asset" in
        sddm) dest=config/includes.chroot/usr/share/sddm/themes;;
        plymouth) dest=config/includes.chroot/usr/share/plymouth/themes;;
        grub) dest=config/includes.binary/boot/grub/themes;;
        plasma) dest=config/includes.chroot/usr/share/plasma;;
    esac
    mkdir -p "$WORK/$dest"
    rsync -a "$ROOT/$asset/" "$WORK/$dest/"
done
rsync -a "$ROOT/installer/calamares/" "$WORK/config/includes.chroot/etc/calamares/"
mkdir -p "$WORK/config/archives"
printf 'deb [trusted=yes] file://%s/packages ./\n' "$WORK" > "$WORK/config/archives/katu-local.list.chroot"
find "$WORK/config/hooks" -type f -name '*.hook.*' -exec chmod 755 {} +
chmod 755 "$WORK/config/includes.chroot/usr/lib/katu/qa-live-smoke"
cd "$WORK"
lb config --distribution "$LB_DISTRIBUTION" --architecture "$LB_ARCHITECTURE" \
    --mirror-bootstrap "$LB_MIRROR_BOOTSTRAP" --mirror-chroot "$LB_MIRROR_CHROOT" \
    --mirror-chroot-security "$LB_MIRROR_CHROOT_SECURITY" --archive-areas "$LB_ARCHIVE_AREAS" \
    --binary-images iso-hybrid --bootloaders "$LB_BOOTLOADERS" --debian-installer none --memtest none \
    --iso-application 'Katu OS' --iso-preparer 'Katu OS Build System' --iso-publisher 'Katu OS' \
    --iso-volume "$LB_ISO_VOLUME" --bootappend-live 'boot=live components username=katu hostname=katu' \
    --compression xz --verbose
lb bootstrap
lb chroot
# live-build diverts /etc/os-release during bootstrap; restore the existing
# Katu identity after it removes that diversion, before packing the rootfs.
install -m 644 "$ROOT/packages/katu-release/etc/os-release" "$WORK/chroot/etc/os-release"
bash "$ROOT/scripts/preflight-check.sh" --root "$WORK/chroot"
lb binary
ISO="$OUT/katu-os-$VERSION-amd64.iso"
test -s "$WORK/live-image-amd64.hybrid.iso"
mv "$WORK/live-image-amd64.hybrid.iso" "$ISO"
bash "$ROOT/scripts/validate-iso.sh" "$ISO"
bash "$ROOT/scripts/test-iso.sh" "$ISO" --timeout 1200
python3 "$ROOT/scripts/release-gate.py" "$ISO" --candidate --commit "$COMMIT" --build-date "$STAMP"
printf '%s\n' "$ISO" > "$ROOT/output/latest-candidate.txt"
echo "Candidate validated automatically: $ISO"
echo 'Manual Live, installation and boot-without-ISO acceptance still required.'
