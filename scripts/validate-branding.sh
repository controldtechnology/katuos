#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-branding.sh — Katu OS Branding Validator
Verifica integridade de todos os assets de branding no projeto.
Uso: python3 scripts/validate-branding.sh
"""
import sys, os
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not found — pip install Pillow")
    sys.exit(1)

ROOT = Path(__file__).parent.parent.resolve()
ERRORS = []
WARNINGS = []
OK = []

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.ico', '.gif'}

def check(path, min_w=0, min_h=0, max_w=99999, max_h=99999,
          exact_w=None, exact_h=None, label='', must_exist=True):
    p = ROOT / path
    suffix = p.suffix.lower()
    if not p.exists():
        if must_exist:
            ERRORS.append(f"MISSING: {path}")
        return
    # For non-image files (conf, qml, desktop, txt, json…) just check existence
    if suffix not in IMAGE_EXTS:
        sz = p.stat().st_size
        if sz == 0:
            ERRORS.append(f"EMPTY: {path}")
        else:
            OK.append(f"  OK  {'FILE':>9s} {sz:>10,}B  {path}")
        return
    try:
        with Image.open(p) as img:
            w, h = img.size
    except Exception as e:
        ERRORS.append(f"CORRUPT: {path} — {e}")
        return

    issues = []
    if exact_w and w != exact_w:
        issues.append(f"width={w} (expected {exact_w})")
    if exact_h and h != exact_h:
        issues.append(f"height={h} (expected {exact_h})")
    if w < min_w:
        issues.append(f"width={w} < min {min_w}")
    if h < min_h:
        issues.append(f"height={h} < min {min_h}")
    if w > max_w:
        WARNINGS.append(f"OVERSIZED: {path} {w}x{h} (max {max_w}x{max_h})")
    if issues:
        ERRORS.append(f"DIMENSION: {path} {w}x{h} — {', '.join(issues)}")
    else:
        sz = p.stat().st_size
        OK.append(f"  OK  {w:4d}x{h:4d} {sz:>10,}B  {path}")

def check_qml_refs(qml_path, image_names):
    """Check that a QML file references expected image names."""
    p = ROOT / qml_path
    if not p.exists():
        ERRORS.append(f"QML MISSING: {qml_path}")
        return
    content = p.read_text(encoding='utf-8', errors='ignore')
    for name in image_names:
        if name not in content:
            WARNINGS.append(f"QML REF NOT FOUND: '{name}' in {qml_path}")

def check_conf_ref(conf_path, key, expected_path_fragment):
    p = ROOT / conf_path
    if not p.exists():
        ERRORS.append(f"CONF MISSING: {conf_path}")
        return
    content = p.read_text(encoding='utf-8', errors='ignore')
    if expected_path_fragment not in content:
        WARNINGS.append(f"CONF: '{key}' not pointing to '{expected_path_fragment}' in {conf_path}")

print("=" * 60)
print("Katu OS Branding Validator")
print("=" * 60)

# ── GRUB ──────────────────────────────────────────────────
print("\n[GRUB]")
for base in [
    'config/includes.binary/boot/grub/themes/katu',
    'config/includes.chroot/boot/grub/themes/katu',
    'grub/katu',
]:
    check(f'{base}/background.png',   min_w=1280, min_h=720, max_w=4096, label='grub-bg')
    check(f'{base}/katu-grub-logo.png', min_w=100, min_h=50, label='grub-logo')
    check(f'{base}/katu-selection.png', min_w=100, label='grub-sel')
    check(f'{base}/theme.txt', label='grub-theme-txt')

# ── Plymouth ──────────────────────────────────────────────
print("\n[Plymouth]")
for base in [
    'config/includes.chroot/usr/share/plymouth/themes/katu',
    'plymouth/katu',
]:
    check(f'{base}/logo.png',          min_w=100, max_w=800, max_h=800, label='plym-logo')
    check(f'{base}/spinner.png',       min_w=64, max_w=2048, label='plym-spinner')
    check(f'{base}/progress-dot.png',  min_w=8, max_w=512, label='plym-dot')
    check(f'{base}/katu.script',       label='plym-script')
    check(f'{base}/katu.plymouth',     label='plym-conf')

# ── SDDM ──────────────────────────────────────────────────
print("\n[SDDM]")
for base in [
    'config/includes.chroot/usr/share/sddm/themes/katu',
    'sddm/katu',
]:
    check(f'{base}/background.png', min_w=1280, min_h=720, max_w=4096, label='sddm-bg')
    check(f'{base}/logo.png',       min_w=100, max_w=2048, label='sddm-logo')
    check(f'{base}/Main.qml',       label='sddm-qml')
    check(f'{base}/theme.conf',     label='sddm-conf')
check_qml_refs('sddm/katu/Main.qml', ['background.png', 'logo.png'])

# ── Plasma Splash ─────────────────────────────────────────
print("\n[Plasma Splash]")
check('config/includes.chroot/usr/share/pixmaps/katu-logo.png',
      min_w=100, max_w=2000, label='pixmaps-logo')
check_qml_refs(
    'config/includes.chroot/usr/share/plasma/look-and-feel/org.katuos.desktop/contents/splash/Splash.qml',
    ['/usr/share/pixmaps/katu-logo.png'])

# ── Wallpapers ────────────────────────────────────────────
print("\n[Wallpapers]")
for name in ['katu-amazonia-4k', 'katu-onca-4k', 'katu-dark-4k',
             'katu-green-4k', 'katu-minimal-4k', 'katu-rio-4k']:
    check(f'config/includes.chroot/usr/share/wallpapers/katu/contents/images/{name}.png',
          min_w=1920, min_h=1080, label=name)
check('config/includes.chroot/usr/share/wallpapers/katu/metadata.json', label='wall-meta')
check_conf_ref(
    'config/includes.chroot/usr/share/plasma/look-and-feel/org.katuos.desktop/contents/defaults',
    'Image', 'katu-amazonia-4k.png')

# ── Calamares ─────────────────────────────────────────────
print("\n[Calamares]")
for base in [
    'config/includes.chroot/etc/calamares/branding/katu',
    'installer/calamares/branding/katu',
]:
    check(f'{base}/logo.png',    min_w=100, max_w=2048, label='cal-logo')
    check(f'{base}/icon.png',    min_w=32, max_w=256, label='cal-icon')
    check(f'{base}/welcome.png', min_w=800, label='cal-welcome')
    for i in range(1, 7):
        check(f'{base}/slide-0{i}.png', min_w=800, label=f'cal-slide{i}')
    check(f'{base}/branding.desc', label='cal-branding-desc')
    check(f'{base}/show.qml',      label='cal-show-qml')
    check(f'{base}/stylesheet.qss', label='cal-stylesheet', must_exist=False)

# ── App Icons ─────────────────────────────────────────────
print("\n[App Icons — hicolor 256x256]")
icons_256 = [
    'katu-backup', 'katu-browser', 'katu-connect', 'katu-drivers',
    'katu-feedback', 'katu-files', 'katu-help', 'katu-home',
    'katu-installer', 'katu-logo', 'katu-security', 'katu-settings',
    'katu-store', 'katu-system-info', 'katu-terminal', 'katu-user',
    'katu-welcome',
]
for icon in icons_256:
    check(f'config/includes.chroot/usr/share/icons/hicolor/256x256/apps/{icon}.png',
          min_w=64, max_w=1024, label=f'icon-{icon}')

# ── Theme Icons ───────────────────────────────────────────
print("\n[Theme Icons — katu]")
for size in [64, 32]:
    for cat, names in [
        ('devices', ['katu-computer', 'katu-network', 'katu-removable-drive', 'katu-usb']),
        ('places',  ['katu-home', 'katu-trash-empty', 'katu-trash-full']),
    ]:
        for name in names:
            check(f'config/includes.chroot/usr/share/icons/katu/{size}x{size}/{cat}/{name}.png',
                  min_w=size//2, max_w=size*2, label=f'{name}-{size}')

# ── Branding Logos ────────────────────────────────────────
print("\n[Branding logos]")
for name in ['katu-os-dark', 'katu-os-white', 'katu-os-monochrome',
             'katu-symbol-white', 'katu-symbol-monochrome']:
    for base in ['branding/logos', 'config/includes.chroot/usr/share/katu/branding/logos']:
        check(f'{base}/{name}.png', min_w=100, label=name)

# ── About Distro ──────────────────────────────────────────
print("\n[About Distro]")
check_conf_ref('config/includes.chroot/etc/xdg/kcm-about-distro.conf',
               'LogoPath', '/usr/share/pixmaps/katu-logo.png')

# ── Desktop Live ─────────────────────────────────────────
print("\n[Live desktop files]")
check('config/includes.chroot/etc/skel/Área de Trabalho/katu-install.desktop', label='live-desktop')
check('config/includes.chroot/usr/share/applications/katu-install.desktop',    label='apps-desktop')

# ── REPORT ───────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"OK:       {len(OK)}")
print(f"WARNINGS: {len(WARNINGS)}")
print(f"ERRORS:   {len(ERRORS)}")
print("=" * 60)

for line in OK:
    print(line)

if WARNINGS:
    print("\nWARNINGS:")
    for w in WARNINGS:
        print(f"  WARN  {w}")

if ERRORS:
    print("\nERRORS:")
    for e in ERRORS:
        print(f"  ERR   {e}")
    print(f"\nValidação FALHOU — {len(ERRORS)} erro(s)")
    sys.exit(1)
else:
    print("\nValidação OK — todos os assets presentes e com dimensões corretas.")
