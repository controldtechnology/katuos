#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync-katu-assets.sh — Katu OS Official Asset Sync
Propaga assets da fonte oficial para todos os destinos do projeto.
Gera derivados (redimensionamentos) sem modificar os arquivos originais.
Uso: python3 scripts/sync-katu-assets.sh [--dry-run]
"""
import sys, os, shutil, hashlib, json
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow não encontrado. Instale: pip install Pillow")
    sys.exit(1)

DRY_RUN = '--dry-run' in sys.argv
ROOT = Path(__file__).parent.parent.resolve()
SRC  = ROOT / 'imagens' / 'katu-os-final-assets'
GEN  = ROOT / 'build' / 'generated-assets'
LOG  = []
ERRORS = []

def log(msg):
    print(msg)
    LOG.append(msg)

def err(msg):
    print(f"  ERROR: {msg}", file=sys.stderr)
    ERRORS.append(msg)

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def copy_image(src, dst, purpose='', resize=None, background=None):
    """Copy or resize image from src to dst. Never modifies src."""
    src, dst = Path(src), Path(dst)
    if not src.exists():
        err(f"Source missing: {src}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if DRY_RUN:
        dims = f" → {resize[0]}x{resize[1]}" if resize else ""
        log(f"  [DRY] {src.name}{dims} → {dst}")
        return True
    try:
        with Image.open(src) as img:
            if resize:
                # Always use LANCZOS for high quality downscaling
                out = img.convert('RGBA') if (img.mode == 'RGBA' or background) else img
                if background:
                    # Composite RGBA onto solid background color
                    bg = Image.new('RGB', img.size, background)
                    if img.mode == 'RGBA':
                        bg.paste(img, mask=img.split()[3])
                    else:
                        bg.paste(img)
                    out = bg
                if isinstance(resize, tuple):
                    out = out.resize(resize, Image.LANCZOS)
                # Preserve alpha if original had it and no background specified
                if background:
                    out = out.convert('RGB')
            else:
                out = img.copy()
            out.save(str(dst), optimize=True)
        dims = f"{out.size[0]}x{out.size[1]}" if resize else "original"
        sz = dst.stat().st_size
        log(f"  [OK] {src.name} → {dst.relative_to(ROOT)} ({dims}, {sz:,}B)")
        return True
    except Exception as e:
        err(f"Failed {src} → {dst}: {e}")
        return False

def copy_raw(src, dst, purpose=''):
    """Copy file as-is without any image processing."""
    src, dst = Path(src), Path(dst)
    if not src.exists():
        err(f"Source missing: {src}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if DRY_RUN:
        log(f"  [DRY] copy {src.name} → {dst}")
        return True
    shutil.copy2(str(src), str(dst))
    sz = dst.stat().st_size
    log(f"  [OK] copy {src.name} → {dst.relative_to(ROOT)} ({sz:,}B)")
    return True

def make_icon(src, size, dst):
    """Scale icon to exact size preserving transparency (RGBA)."""
    src, dst = Path(src), Path(dst)
    if not src.exists():
        err(f"Icon source missing: {src}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if DRY_RUN:
        log(f"  [DRY] icon {src.name} → {dst} ({size}x{size})")
        return True
    try:
        with Image.open(src) as img:
            # Ensure RGBA for proper icon with transparency
            if img.mode == 'RGB':
                # RGB app icons — keep as RGBA with white bg for consistency
                out = img.resize((size, size), Image.LANCZOS)
                # Convert to RGBA
                out = out.convert('RGBA')
            else:
                out = img.convert('RGBA').resize((size, size), Image.LANCZOS)
            out.save(str(dst), optimize=True)
        log(f"  [OK] icon {src.name} {size}px → {dst.relative_to(ROOT)}")
        return True
    except Exception as e:
        err(f"Icon failed {src}: {e}")
        return False

MANIFEST = []

def record(src, dst, purpose):
    MANIFEST.append({
        "source": str(src),
        "destination": str(dst),
        "sha256": sha256(str(dst)) if Path(dst).exists() and not DRY_RUN else "",
        "width": 0, "height": 0,
        "purpose": purpose
    })

# ─────────────────────────────────────────────────────────
# SOURCES
# ─────────────────────────────────────────────────────────
LOGO_WHITE      = SRC / 'branding/logo/katu-os-white.png'       # 1800x600 RGBA horiz
LOGO_DARK       = SRC / 'branding/logo/katu-os-dark.png'        # 1800x600 RGBA horiz
LOGO_MONO       = SRC / 'branding/logo/katu-os-monochrome.png'  # 1800x600 RGBA horiz
SYMBOL_WHITE    = SRC / 'branding/logo/katu-symbol-white.png'   # 1024x1024 RGBA
SYMBOL_MONO     = SRC / 'branding/logo/katu-symbol-monochrome.png' # 1024x1024 RGBA
GRUB_LOGO       = SRC / 'grub/katu-grub-logo.png'              # 1000x320 RGBA
GRUB_SEL        = SRC / 'grub/katu-selection.png'              # 1400x120 RGBA
PLYM_LOGO       = SRC / 'plymouth/katu/katu-logo-boot-light.png' # 1024x1024 RGBA
PLYM_SPINNER    = SRC / 'plymouth/katu/spinner.png'             # 512x512 RGBA
PLYM_DOT        = SRC / 'plymouth/katu/progress-dot.png'       # 128x128 RGBA
WALL_AMAZONIA   = SRC / 'wallpapers/katu-amazonia-4k.png'       # 3840x2160
WALL_ONCA       = SRC / 'wallpapers/katu-onca-4k.png'
WALL_DARK       = SRC / 'wallpapers/katu-dark-4k.png'
WALL_GREEN      = SRC / 'wallpapers/katu-green-4k.png'
WALL_MINIMAL    = SRC / 'wallpapers/katu-minimal-4k.png'
WALL_RIO        = SRC / 'wallpapers/katu-rio-4k.png'
CAL_WELCOME     = SRC / 'installer/live/katu-live-welcome.png'  # 1920x1080
SLIDES          = [SRC / f'installer/calamares/slides/slide-0{i}.png' for i in range(1,7)]
APP_BACKUP      = SRC / 'applications/katu-backup.png'          # 1024x1024 RGB
APP_FEEDBACK    = SRC / 'applications/katu-feedback.png'
APP_SECURITY    = SRC / 'applications/katu-security.png'
APP_SYSINFO     = SRC / 'applications/katu-system-info.png'
ICON_COMPUTER   = SRC / 'plasma/icons/katu-computer.png'        # 1024x1024 RGB
ICON_HOME       = SRC / 'plasma/icons/katu-home.png'
ICON_NETWORK    = SRC / 'plasma/icons/katu-network.png'
ICON_REMOVABLE  = SRC / 'plasma/icons/katu-removable-drive.png'
ICON_TRASH_E    = SRC / 'plasma/icons/katu-trash-empty.png'
ICON_TRASH_F    = SRC / 'plasma/icons/katu-trash-full.png'
ICON_USB        = SRC / 'plasma/icons/katu-usb.png'

# ─────────────────────────────────────────────────────────
# GRUB BACKGROUND — generate from wallpaper
# ─────────────────────────────────────────────────────────
log("\n=== GRUB ===")
GRUB_BG_GEN = GEN / 'grub/background.png'
copy_image(WALL_AMAZONIA, GRUB_BG_GEN, 'grub-background', resize=(1920, 1080))

GRUB_DESTS = [
    ROOT / 'grub/katu/background.png',
    ROOT / 'config/includes.binary/boot/grub/themes/katu/background.png',
    ROOT / 'config/includes.chroot/boot/grub/themes/katu/background.png',
]
for dst in GRUB_DESTS:
    copy_raw(GRUB_BG_GEN, dst, 'grub-background')

# GRUB logo and selection (already correct from official source)
for dst in [
    ROOT / 'grub/katu/katu-grub-logo.png',
    ROOT / 'config/includes.binary/boot/grub/themes/katu/katu-grub-logo.png',
    ROOT / 'config/includes.chroot/boot/grub/themes/katu/katu-grub-logo.png',
]:
    copy_raw(GRUB_LOGO, dst, 'grub-logo')

for dst in [
    ROOT / 'grub/katu/katu-selection.png',
    ROOT / 'config/includes.binary/boot/grub/themes/katu/katu-selection.png',
    ROOT / 'config/includes.chroot/boot/grub/themes/katu/katu-selection.png',
]:
    copy_raw(GRUB_SEL, dst, 'grub-selection')

# ─────────────────────────────────────────────────────────
# PLYMOUTH — scale logo to 300x300 for screen fit
# ─────────────────────────────────────────────────────────
log("\n=== Plymouth ===")
PLYM_LOGO_GEN = GEN / 'plymouth/logo.png'
copy_image(PLYM_LOGO, PLYM_LOGO_GEN, 'plymouth-logo', resize=(300, 300))

for dst in [
    ROOT / 'plymouth/katu/logo.png',
    ROOT / 'config/includes.chroot/usr/share/plymouth/themes/katu/logo.png',
]:
    copy_raw(PLYM_LOGO_GEN, dst, 'plymouth-logo')

# katu-logo-boot-light stays as official size (1024x1024 - used as alternate)
for dst in [
    ROOT / 'plymouth/katu/katu-logo-boot-light.png',
    ROOT / 'config/includes.chroot/usr/share/plymouth/themes/katu/katu-logo-boot-light.png',
]:
    copy_raw(PLYM_LOGO, dst, 'plymouth-logo-light')

# Spinner (512x512 single-frame RGBA — correct as-is)
for dst in [
    ROOT / 'plymouth/katu/spinner.png',
    ROOT / 'config/includes.chroot/usr/share/plymouth/themes/katu/spinner.png',
]:
    copy_raw(PLYM_SPINNER, dst, 'plymouth-spinner')

# Progress dot
for dst in [
    ROOT / 'plymouth/katu/progress-dot.png',
    ROOT / 'config/includes.chroot/usr/share/plymouth/themes/katu/progress-dot.png',
]:
    copy_raw(PLYM_DOT, dst, 'plymouth-dot')

# ─────────────────────────────────────────────────────────
# SDDM — background 1920x1080, logo horizontal
# ─────────────────────────────────────────────────────────
log("\n=== SDDM ===")
SDDM_BG_GEN = GEN / 'sddm/background.png'
copy_image(WALL_AMAZONIA, SDDM_BG_GEN, 'sddm-background', resize=(1920, 1080))

# SDDM logo: horizontal white logo scaled to 330x110 (3:1 → fits QML 110x44)
SDDM_LOGO_GEN = GEN / 'sddm/logo.png'
copy_image(LOGO_WHITE, SDDM_LOGO_GEN, 'sddm-logo', resize=(330, 110))

for dst in [
    ROOT / 'sddm/katu/background.png',
    ROOT / 'config/includes.chroot/usr/share/sddm/themes/katu/background.png',
]:
    copy_raw(SDDM_BG_GEN, dst, 'sddm-background')

for dst in [
    ROOT / 'sddm/katu/logo.png',
    ROOT / 'config/includes.chroot/usr/share/sddm/themes/katu/logo.png',
]:
    copy_raw(SDDM_LOGO_GEN, dst, 'sddm-logo')

# ─────────────────────────────────────────────────────────
# PLASMA SPLASH — pixmaps logo (displayed at 180x72 in QML)
# ─────────────────────────────────────────────────────────
log("\n=== Plasma Splash / pixmaps ===")
PIXMAP_LOGO_GEN = GEN / 'pixmaps/katu-logo.png'
copy_image(LOGO_WHITE, PIXMAP_LOGO_GEN, 'pixmaps-logo', resize=(360, 120))

for dst in [
    ROOT / 'config/includes.chroot/usr/share/pixmaps/katu-logo.png',
]:
    copy_raw(PIXMAP_LOGO_GEN, dst, 'pixmaps-logo')

# ─────────────────────────────────────────────────────────
# WALLPAPERS — 4K originals → wallpaper dirs
# ─────────────────────────────────────────────────────────
log("\n=== Wallpapers ===")
wall_pairs = [
    (WALL_AMAZONIA, 'katu-amazonia-4k.png'),
    (WALL_ONCA,     'katu-onca-4k.png'),
    (WALL_DARK,     'katu-dark-4k.png'),
    (WALL_GREEN,    'katu-green-4k.png'),
    (WALL_MINIMAL,  'katu-minimal-4k.png'),
    (WALL_RIO,      'katu-rio-4k.png'),
]
WALL_CONFIG = ROOT / 'config/includes.chroot/usr/share/wallpapers/katu/contents/images'
WALL_TOPLEVEL = ROOT / 'wallpapers'

for src_path, name in wall_pairs:
    copy_raw(src_path, WALL_CONFIG / name, 'wallpaper')
    copy_raw(src_path, WALL_TOPLEVEL / name, 'wallpaper-source')

# ─────────────────────────────────────────────────────────
# CALAMARES BRANDING — logo, icon, welcome
# ─────────────────────────────────────────────────────────
log("\n=== Calamares branding ===")
# Logo: white horizontal (sidebar)
CAL_LOGO_GEN = GEN / 'calamares/logo.png'
copy_image(LOGO_WHITE, CAL_LOGO_GEN, 'calamares-logo', resize=(400, 133))

# Icon: square symbol for window title bar
CAL_ICON_GEN = GEN / 'calamares/icon.png'
copy_image(SYMBOL_WHITE, CAL_ICON_GEN, 'calamares-icon', resize=(64, 64))

# Welcome: full 1920x1080 imagery
for dst in [
    ROOT / 'config/includes.chroot/etc/calamares/branding/katu/logo.png',
    ROOT / 'installer/calamares/branding/katu/logo.png',
]:
    copy_raw(CAL_LOGO_GEN, dst, 'calamares-logo')

for dst in [
    ROOT / 'config/includes.chroot/etc/calamares/branding/katu/icon.png',
    ROOT / 'installer/calamares/branding/katu/icon.png',
]:
    copy_raw(CAL_ICON_GEN, dst, 'calamares-icon')

for dst in [
    ROOT / 'config/includes.chroot/etc/calamares/branding/katu/welcome.png',
    ROOT / 'installer/calamares/branding/katu/welcome.png',
]:
    copy_raw(CAL_WELCOME, dst, 'calamares-welcome')

# ─────────────────────────────────────────────────────────
# CALAMARES SLIDES
# ─────────────────────────────────────────────────────────
log("\n=== Calamares slides ===")
for i, slide_src in enumerate(SLIDES, 1):
    name = f'slide-0{i}.png'
    for dst in [
        ROOT / f'config/includes.chroot/etc/calamares/branding/katu/{name}',
        ROOT / f'installer/calamares/branding/katu/{name}',
    ]:
        copy_raw(slide_src, dst, f'calamares-slide-{i:02d}')

# ─────────────────────────────────────────────────────────
# BRANDING LOGOS — system-wide
# ─────────────────────────────────────────────────────────
log("\n=== Branding logos ===")
logo_map = [
    (LOGO_DARK,   'katu-os-dark.png'),
    (LOGO_MONO,   'katu-os-monochrome.png'),
    (LOGO_WHITE,  'katu-os-white.png'),
    (SYMBOL_MONO, 'katu-symbol-monochrome.png'),
    (SYMBOL_WHITE,'katu-symbol-white.png'),
]
for src_path, name in logo_map:
    for dst in [
        ROOT / 'branding/logos' / name,
        ROOT / 'config/includes.chroot/usr/share/katu/branding/logos' / name,
    ]:
        copy_raw(src_path, dst, 'branding-logo')

# ─────────────────────────────────────────────────────────
# APP ICONS — hicolor (256x256, 128x128, 64x64, 48x48)
# ─────────────────────────────────────────────────────────
log("\n=== App icons (hicolor) ===")
# Icons with dedicated official sources
APP_ICON_MAP = {
    'katu-backup':      APP_BACKUP,
    'katu-feedback':    APP_FEEDBACK,
    'katu-security':    APP_SECURITY,
    'katu-system-info': APP_SYSINFO,
}
# Icons using Katu symbol (official brand mark) as base
SYMBOL_ICON_MAP = {
    'katu-logo':        PLYM_LOGO,   # official boot logo = brand mark
    'katu-installer':   PLYM_LOGO,
    'katu-browser':     SYMBOL_WHITE,
    'katu-connect':     SYMBOL_WHITE,
    'katu-drivers':     SYMBOL_WHITE,
    'katu-files':       SYMBOL_WHITE,
    'katu-help':        SYMBOL_WHITE,
    'katu-home':        ICON_HOME,
    'katu-settings':    SYMBOL_WHITE,
    'katu-store':       SYMBOL_WHITE,
    'katu-terminal':    SYMBOL_WHITE,
    'katu-user':        SYMBOL_WHITE,
    'katu-welcome':     LOGO_DARK,
}
ALL_APP_ICONS = {**APP_ICON_MAP, **SYMBOL_ICON_MAP}

HICOLOR = ROOT / 'config/includes.chroot/usr/share/icons/hicolor'
for icon_name, src_path in ALL_APP_ICONS.items():
    for size in [256, 128, 64, 48]:
        dst = HICOLOR / f'{size}x{size}/apps/{icon_name}.png'
        if dst.exists() or size == 256:  # Always generate 256; others only if dir exists
            make_icon(src_path, size, dst)

# ─────────────────────────────────────────────────────────
# THEME ICONS — katu (places + devices, 32 and 64)
# ─────────────────────────────────────────────────────────
log("\n=== Theme icons (katu places/devices) ===")
KATU_ICONS = ROOT / 'config/includes.chroot/usr/share/icons/katu'
PLASMA_ICONS = ROOT / 'plasma/icons/katu'

device_map = [
    (ICON_COMPUTER,  'katu-computer',       'devices'),
    (ICON_NETWORK,   'katu-network',        'devices'),
    (ICON_REMOVABLE, 'katu-removable-drive','devices'),
    (ICON_USB,       'katu-usb',            'devices'),
    (ICON_HOME,      'katu-home',           'places'),
    (ICON_TRASH_E,   'katu-trash-empty',    'places'),
    (ICON_TRASH_F,   'katu-trash-full',     'places'),
]

for src_path, name, category in device_map:
    for size in [64, 32]:
        for base in [KATU_ICONS, PLASMA_ICONS]:
            dst = base / f'{size}x{size}/{category}/{name}.png'
            make_icon(src_path, size, dst)

# ─────────────────────────────────────────────────────────
# WRITE MANIFEST
# ─────────────────────────────────────────────────────────
log("\n=== Writing manifest ===")
if not DRY_RUN:
    GEN.mkdir(parents=True, exist_ok=True)
    manifest_path = GEN / 'MANIFEST.json'
    # Build manifest from what was actually copied
    manifest_data = []
    for dst_path in GEN.rglob('*'):
        if dst_path.is_file() and dst_path.suffix in ('.png', '.jpg'):
            try:
                with Image.open(dst_path) as img:
                    w, h = img.size
            except:
                w = h = 0
            manifest_data.append({
                "generated": str(dst_path.relative_to(ROOT)),
                "sha256": sha256(str(dst_path)),
                "width": w,
                "height": h,
            })
    with open(manifest_path, 'w') as f:
        json.dump(manifest_data, f, indent=2)
    log(f"  [OK] Manifest: {manifest_path}")

# ─────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────
print("\n" + "="*60)
ok_count = sum(1 for l in LOG if '[OK]' in l)
err_count = len(ERRORS)
print(f"Assets processados: {ok_count}")
print(f"Erros: {err_count}")
if ERRORS:
    print("\nErros encontrados:")
    for e in ERRORS:
        print(f"  - {e}")
if DRY_RUN:
    print("\n[DRY RUN] Nenhum arquivo foi modificado.")
else:
    print("\nSincronização concluída.")
