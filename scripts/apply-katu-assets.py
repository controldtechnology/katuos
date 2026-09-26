#!/usr/bin/env python3
"""
Apply ALL Katu OS visual assets to the build config.

Sources:
  imagens/ChatGPT Image 20 de set. de 2026, *.png  — photorealistic wallpapers + app icons
  imagens/katu-os-final-assets/                     — organized final pack (GRUB, Plymouth, Calamares, system icons)
  imagens/site-*.png                                — official branding downloaded from katuos.com.br

Targets (all under config/includes.chroot/ or config/includes.binary/):
  wallpapers, SDDM, GRUB, Plymouth, hicolor icons, katu icon theme, Calamares, branding
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
PKG  = SRC / "katu-os-final-assets"
INC  = REPO / "config" / "includes.chroot"
BINC = REPO / "config" / "includes.binary"


def img(ts):
    return SRC / f"ChatGPT Image 20 de set. de 2026, {ts}.png"

def site(name):
    return SRC / f"site-{name}"

def pack(*parts):
    return PKG.joinpath(*parts)


def process(src: Path, dst: Path, size=None, mode="RGBA"):
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert(mode)
    if size:
        im = im.resize(size, Image.LANCZOS)
    im.save(dst, "PNG", optimize=False)
    label = f"{size[0]}x{size[1]}" if size else "orig"
    print(f"  ✓  {src.name[:48]:48s} → {str(dst.relative_to(REPO))[:60]} [{label}]")


def copy(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  ✓  {src.name[:48]:48s} → {str(dst.relative_to(REPO))[:60]} [copy]")


# ─────────────────────────────────────────────────────────────────────────────
# 1. WALLPAPERS  6 × 1920×1080
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 1. Wallpapers ──")

WP = INC / "usr/share/wallpapers/katu/contents/images"

WALLPAPERS = {
    # Main: clean photorealistic jaguar+Amazon at sunset — no text overlay
    "katu-amazonia-4k.png": img("17_12_03"),
    # Hero: same scene with "KATU OS / TECNOLOGIA BRASILEIRA" branding text
    "katu-onca-4k.png":     img("16_55_58"),
    # Jaguar in Amazon jungle + waterfall — SDDM background
    "katu-selva-4k.png":    img("17_00_19"),
    # River panorama — misty Amazon morning
    "katu-rio-4k.png":      img("17_26_25"),
    # Green Amazônia — lush canopy scene
    "katu-green-4k.png":    img("17_20_02"),
    # Dark — abstract dark green + gold swirls + jaguar silhouette
    "katu-dark-4k.png":     img("17_11_00"),
    # Minimal modern — second Amazon panorama variant
    "katu-minimal-4k.png":  img("17_14_37"),
    # Branding panorama dark — "KATU OS" text + jaguar + Amazon
    "katu-brand-dark-4k.png": img("17_18_35"),
    # Branding panorama full — "KATU OS" + features list + jaguar
    "katu-brand-full-4k.png": img("17_23_58"),
}

for name, src in WALLPAPERS.items():
    process(src, WP / name, (1920, 1080))

# ─────────────────────────────────────────────────────────────────────────────
# 2. SDDM  background + logo
#    Written to both includes.chroot/ AND sddm/ source dir (rsync override)
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 2. SDDM ──")

SDDM_DIRS = [
    INC / "usr/share/sddm/themes/katu",
    REPO / "sddm/katu",
]
for d in SDDM_DIRS:
    # Jaguar in Amazon jungle — matches SDDM mockup (20_36_58.png)
    process(img("17_00_19"), d / "background.png", (1920, 1080))
    # Horizontal official logo: leaf+jaguar icon + "KATU OS" lettering
    # QML renders at 110×44 with PreserveAspectFit — supply 2× source for sharpness
    process(site("logo-horizontal-wide.png"), d / "logo.png", (220, 88))

# ─────────────────────────────────────────────────────────────────────────────
# 3. GRUB  background + logo + selection highlight
#    Written to chroot/, binary/ AND grub/ source dir (rsync → binary/)
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 3. GRUB ──")

GRUB_DIRS = [
    INC / "boot/grub/themes/katu",
    BINC / "boot/grub/themes/katu",
    REPO / "grub/katu",
]
for d in GRUB_DIRS:
    # GRUB requires RGB (no alpha channel)
    process(img("17_12_03"), d / "background.png", (1920, 1080), mode="RGB")
    copy(pack("grub", "katu-grub-logo.png"), d / "katu-grub-logo.png")
    copy(pack("grub", "katu-selection.png"), d / "katu-selection.png")

# ─────────────────────────────────────────────────────────────────────────────
# 4. PLYMOUTH  logo + spinner + progress-dot + boot-light logo
#    Written to chroot/ AND plymouth/ source dir
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 4. Plymouth ──")

PLY_DIRS = [
    INC / "usr/share/plymouth/themes/katu",
    REPO / "plymouth/katu",
]
for d in PLY_DIRS:
    # Central boot logo: circular jaguar+leaf+gold ring
    process(img("17_41_29"), d / "logo.png", (256, 256))
    copy(pack("plymouth", "katu", "katu-logo-boot-light.png"), d / "katu-logo-boot-light.png")
    copy(pack("plymouth", "katu", "progress-dot.png"),         d / "progress-dot.png")
    copy(pack("plymouth", "katu", "spinner.png"),              d / "spinner.png")

# ─────────────────────────────────────────────────────────────────────────────
# 5. APP ICONS — hicolor  256 / 128 / 64 / 48 px
#    All katu-branded app icons from the ChatGPT photorealistic set
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 5. App icons (hicolor) ──")

ICON_SOURCES = {
    "katu-logo":        img("17_10_00"),   # circular jaguar+leaf emblem — clean icon (no text)
    "katu-welcome":     img("17_07_40"),   # rounded-square KATU OS app icon — welcome screen
    "katu-home":        img("17_42_37"),   # jaguar+home symbol (Katu Home app)
    "katu-store":       img("17_43_50"),   # shopping bag + jaguar (Katu Store)
    "katu-backup":      img("17_48_29"),   # circular arrows + jaguar (backup/update)
    "katu-settings":    img("17_50_02"),   # gear + jaguar (system settings)
    "katu-system-info": img("17_52_31"),   # "i" info badge + jaguar
    "katu-feedback":    img("17_52_31"),   # reuse info icon for feedback
    "katu-security":    img("17_52_31"),   # reuse info icon for security
    "katu-files":       img("18_00_02"),   # folder stack + jaguar (file manager)
    "katu-browser":     img("18_02_16"),   # globe + cursor (Katu browser)
    "katu-terminal":    img("18_36_08"),   # terminal window "> _ Katu OS"
    "katu-connect":     img("19_31_46"),   # phone+laptop wireless (Katu Connect)
    "katu-help":        img("19_38_50"),   # book "Ajuda e Documentação" + ?
    "katu-installer":   img("19_41_56"),   # HDD + down arrow (Calamares installer)
    "katu-drivers":     img("19_47_41"),   # chip + driver list (driver manager)
    "katu-user":        img("19_51_22"),   # user silhouette + jaguar (accounts)
}

for sz in [256, 128, 64, 48]:
    dst_dir = INC / f"usr/share/icons/hicolor/{sz}x{sz}/apps"
    for name, src in ICON_SOURCES.items():
        process(src, dst_dir / f"{name}.png", (sz, sz))

# ─────────────────────────────────────────────────────────────────────────────
# 6. KATU ICON THEME  — apps only; places/devices inherit from breeze-dark
#    Desktop icons (Pasta Pessoal, Lixeira, Computador, Rede) use breeze-dark
#    as shown in the official desktop mockup (20_37_56.png).
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 6. Katu icon theme (apps only — places/devices use breeze-dark) ──")

KATU_THEME = INC / "usr/share/icons/katu"

# Remove stale places/devices overrides that were generated by previous runs
import shutil as _shutil
for _sz in ["256x256", "128x128", "64x64", "48x48"]:
    for _cat in ["places", "devices"]:
        _d = KATU_THEME / _sz / _cat
        if _d.exists():
            _shutil.rmtree(_d)
            print(f"  ✗  removed stale {_sz}/{_cat}/")

# App icons into katu theme (kickoff menu + app launcher use these)
for sz in [256, 128, 64, 48]:
    for name, src in ICON_SOURCES.items():
        process(src, KATU_THEME / f"{sz}x{sz}/apps/{name}.png", (sz, sz))

# katu theme index.theme — only apps; everything else falls through to breeze-dark
SIZES = "256x256,128x128,64x64,48x48"
dirs_apps = ",".join(f"{s}/apps" for s in SIZES.split(","))

INDEX = f"""\
[Icon Theme]
Name=Katu
Comment=Katu OS Icon Theme — Amazônia style
Inherits=breeze-dark,hicolor
Directories={dirs_apps}

"""
for sz in SIZES.split(","):
    n = sz.split("x")[0]
    INDEX += f"[{sz}/apps]\nSize={n}\nContext=Applications\nType=Fixed\n\n"

index_path = KATU_THEME / "index.theme"
index_path.parent.mkdir(parents=True, exist_ok=True)
index_path.write_text(INDEX)
print(f"  ✓  katu/index.theme written (apps only — breeze-dark handles places/devices)")

# ─────────────────────────────────────────────────────────────────────────────
# 7. CALAMARES BRANDING  logo + icon + welcome + 6 slides
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 7. Calamares branding ──")

CAL = INC / "etc/calamares/branding/katu"

# Product logo (shown in wizard header bar): wide horizontal logo
process(site("logo-horizontal-wide.png"), CAL / "logo.png", (300, 120))
# Product icon (shown in taskbar / About): circular jaguar icon
process(img("17_41_29"), CAL / "icon.png", (96, 96))
# Welcome background — jaguar in Amazon jungle (matches installer mockup 20_35_40.png)
process(img("17_00_19"), CAL / "welcome.png", (1024, 576))

# 6 installation slides — generated from real Katu photorealistic images
SLIDE_SOURCES = [
    img("17_12_03"),                     # 01 jaguar+Amazon sunset
    img("16_55_58"),                     # 02 hero KATU OS text
    img("18_02_16"),                     # 03 globe+cursor browser
    img("17_48_29"),                     # 04 circular backup+jaguar
    site("brasil-onca-horizonte.png"),   # 05 panorama Brasil
    img("17_26_25"),                     # 06 river Amazon
]
for i, src in enumerate(SLIDE_SOURCES, 1):
    process(src, CAL / f"slide-{i:02d}.png", (1280, 720), mode="RGB")

# ─────────────────────────────────────────────────────────────────────────────
# 8. LIVE WELCOME IMAGE  + branding assets
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 8. Live welcome + branding ──")

BRAND = INC / "usr/share/katu/branding"

copy(pack("installer", "live", "katu-live-welcome.png"), BRAND / "katu-live-welcome.png")

LOGO_VARIANTS = {
    "katu-logo-dark.png":           pack("branding", "logo", "katu-os-dark.png"),
    "katu-logo-white.png":          pack("branding", "logo", "katu-os-white.png"),
    "katu-logo-mono.png":           pack("branding", "logo", "katu-os-monochrome.png"),
    "katu-symbol-white.png":        pack("branding", "logo", "katu-symbol-white.png"),
    "katu-symbol-mono.png":         pack("branding", "logo", "katu-symbol-monochrome.png"),
    "katu-logo-horizontal.png":     site("logo-horizontal-wide.png"),
    "katu-emblema.png":             site("emblema-onca.png"),
    "hero-onca-amazonia.png":       site("hero-onca-amazonia.png"),
    # Extra logo variants from imagens/
    "katu-logo-oficial.png":        SRC / "ChatGPT Image 18 de set. de 2026, 10_15_30.png",  # official logo, white bg
    "katu-logo-oficial-alt.png":    img("16_56_37"),   # same style, variant
    "katu-icon-app.png":            img("17_07_40"),   # rounded-square app icon
    "katu-icon-app-alt.png":        img("17_07_45"),   # same, variant
    "katu-icon-circular.png":       img("17_10_00"),   # circular emblem, dark bg
    "katu-logo-3d-dark.png":        img("17_28_47"),   # 3D logo on marble bg
    "katu-logo-3d-wide.png":        img("17_29_41"),   # wide 3D logo variant
    "katu-logo-horizontal-alt.png": img("17_40_28"),   # horizontal logo, white bg
    "katu-logo-full-br.png":        img("17_01_42"),   # full logo, white + tagline
    # Mockup reference images (for documentation/about screen)
    "katu-sddm-mockup.png":         img("20_36_58"),   # SDDM design reference
    "katu-desktop-mockup.png":      img("20_37_56"),   # desktop design reference
    "katu-installer-mockup.png":    img("20_35_40"),   # installer design reference
    "katu-sddm-alt-mockup.png":     img("19_53_25"),   # SDDM alt design reference
    "katu-desktop-alt-mockup.png":  img("19_54_29"),   # desktop alt reference
}
for name, src in LOGO_VARIANTS.items():
    copy(src, BRAND / name)

print("\n✅  All Katu OS assets applied successfully.\n")
