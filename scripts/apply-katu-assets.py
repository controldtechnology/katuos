#!/usr/bin/env python3
"""
Apply Katu OS visual assets from C:\katuos\imagens to the build config.

Maps each ChatGPT-generated image to its target slot:
  - 6 wallpapers (1672x941 → 1920x1080 Lanczos)
  - App icons 256x256 (1254x1254 → 256x256 Lanczos)
  - Logo variants 128/64/48px
  - SDDM background
  - GRUB background
  - Fixes plasmarc Theme=katu → Theme=default
  - Writes plasma-org.kde.plasma.desktop-appletsrc skel
"""

import sys
import shutil
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
SRC  = REPO / "imagens"
INC  = REPO / "config" / "includes.chroot"

# ── Source image lookup by timestamp suffix ──────────────────────────────────

def img(ts):
    """Return Path to 'ChatGPT Image 20 de set. de 2026, HH_MM_SS.png'"""
    return SRC / f"ChatGPT Image 20 de set. de 2026, {ts}.png"

def img18(ts):
    """18 de set images (logo horizontal)"""
    return SRC / f"ChatGPT Image 18 de set. de 2026, {ts}.png"

# ── Helper: resize and save ───────────────────────────────────────────────────

def process(src: Path, dst: Path, size: tuple):
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGBA")
    im = im.resize(size, Image.LANCZOS)
    # GRUB needs RGB PNG; everything else is fine as RGBA
    if dst.suffix.lower() == ".png":
        im.save(dst, "PNG", optimize=False)
    else:
        im.save(dst)
    print(f"  ✓  {src.name}  →  {dst.relative_to(REPO)}  {size}")

# ── 1. Wallpapers ─────────────────────────────────────────────────────────────

WALLPAPER_DIR = INC / "usr/share/wallpapers/katu/contents/images"

# Primary wallpaper — pure photorealistic jaguar+Amazon (no text overlay)
# 17_12_03: jaguar on branch overlooking Amazon river canyon at sunset
process(img("17_12_03"), WALLPAPER_DIR / "katu-amazonia-4k.png",  (1920, 1080))

# Secondary wallpapers
process(img("16_55_58"), WALLPAPER_DIR / "katu-onca-4k.png",     (1920, 1080))
process(img("17_26_25"), WALLPAPER_DIR / "katu-rio-4k.png",      (1920, 1080))
process(img("17_20_02"), WALLPAPER_DIR / "katu-green-4k.png",    (1920, 1080))
process(img("17_11_00"), WALLPAPER_DIR / "katu-dark-4k.png",     (1920, 1080))
process(img("17_14_37"), WALLPAPER_DIR / "katu-minimal-4k.png",  (1920, 1080))

# ── 2. SDDM background ────────────────────────────────────────────────────────

SDDM_DIR = INC / "usr/share/sddm/themes/katu"
process(img("17_12_03"), SDDM_DIR / "background.png", (1920, 1080))

# ── 3. GRUB background ────────────────────────────────────────────────────────

GRUB_DIR = INC / "boot/grub/themes/katu"
grub_src = img("17_12_03")
grub_dst = GRUB_DIR / "background.png"
grub_dst.parent.mkdir(parents=True, exist_ok=True)
im = Image.open(grub_src).convert("RGB")  # GRUB requires RGB
im = im.resize((1920, 1080), Image.LANCZOS)
im.save(grub_dst, "PNG")
print(f"  ✓  GRUB background  →  {grub_dst.relative_to(REPO)}  (1920x1080 RGB)")

# ── 4. App icons 256×256 ─────────────────────────────────────────────────────

ICONS_256 = INC / "usr/share/icons/hicolor/256x256/apps"

ICON_MAP_256 = {
    "katu-logo.png":        img("17_41_29"),   # circular jaguar+leaf
    "katu-welcome.png":     img("17_41_29"),   # same logo for welcome
    "katu-home.png":        img("17_42_37"),   # jaguar+home symbol
    "katu-store.png":       img("17_43_50"),   # jaguar+bag (store)
    "katu-backup.png":      img("17_48_29"),   # circular arrows (update/backup)
    "katu-settings.png":    img("17_50_02"),   # gear (settings)
    "katu-system-info.png": img("17_52_31"),   # i badge (system info)
    "katu-feedback.png":    img("17_52_31"),   # i badge (feedback)
    "katu-security.png":    img("17_52_31"),   # i badge (security/info)
    "katu-files.png":       img("18_00_02"),   # folder (file manager)
    "katu-browser.png":     img("18_02_16"),   # globe+cursor (browser)
    "katu-terminal.png":    img("18_36_08"),   # terminal "Katu OS"
    "katu-connect.png":     img("19_31_46"),   # phone+laptop wireless
    "katu-help.png":        img("19_38_50"),   # book "Ajuda e Documentação"
    "katu-installer.png":   img("19_41_56"),   # HDD+arrow (installer)
    "katu-drivers.png":     img("19_47_41"),   # chip+drivers list
    "katu-user.png":        img("19_51_22"),   # user silhouette+jaguar
}

for name, src in ICON_MAP_256.items():
    process(src, ICONS_256 / name, (256, 256))

# ── 5. Logo at smaller sizes ─────────────────────────────────────────────────

LOGO_SRC = img("17_41_29")
process(LOGO_SRC, INC / "usr/share/icons/hicolor/128x128/apps/katu-logo.png", (128, 128))
process(LOGO_SRC, INC / "usr/share/icons/hicolor/64x64/apps/katu-logo.png",   (64,  64))
process(LOGO_SRC, INC / "usr/share/icons/hicolor/48x48/apps/katu-logo.png",   (48,  48))

# ── 6. Calamares branding slideshow image ────────────────────────────────────

CAL_BRAND = INC / "etc/calamares/branding/katu"
if CAL_BRAND.exists():
    process(img("17_12_03"), CAL_BRAND / "welcome.png", (1024, 576))
    print("  ✓  Calamares welcome slide updated")

# ── 7. Plymouth splash logo ───────────────────────────────────────────────────

PLYMOUTH_DIR = INC / "usr/share/plymouth/themes/katu"
if PLYMOUTH_DIR.exists():
    process(LOGO_SRC, PLYMOUTH_DIR / "logo.png", (256, 256))
    print("  ✓  Plymouth logo updated")

# ── 8. SDDM logo (the small logo shown in login UI) ──────────────────────────

process(LOGO_SRC, SDDM_DIR / "logo.png", (110, 44))

print("\nAll assets processed successfully.")
