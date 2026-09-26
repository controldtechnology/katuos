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
    # River panorama — misty Amazon morning
    "katu-rio-4k.png":      img("17_26_25"),
    # Green Amazônia — lush canopy scene
    "katu-green-4k.png":    img("17_20_02"),
    # Dark — abstract dark green + gold swirls + jaguar silhouette
    "katu-dark-4k.png":     img("17_11_00"),
    # Minimal modern — second Amazon panorama variant
    "katu-minimal-4k.png":  img("17_14_37"),
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
    process(img("17_12_03"), d / "background.png", (1920, 1080))
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
    "katu-logo":        img("17_41_29"),   # circular jaguar+leaf+gold ring — system logo
    "katu-welcome":     img("17_41_29"),   # same as logo for welcome screen
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
# 6. KATU ICON THEME  — inherits breeze-dark, overrides places + devices
#    Desktop icons: Pasta Pessoal, Lixeira, Computador, Rede
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 6. Katu icon theme (places + devices) ──")

KATU_THEME = INC / "usr/share/icons/katu"

# Map: final-assets source → (hicolor-category, standard KDE icon name)
SYSTEM_ICONS = {
    "katu-home.png":            ("places",  "user-home"),
    "katu-computer.png":        ("devices", "computer"),
    "katu-network.png":         ("places",  "network-workgroup"),
    "katu-removable-drive.png": ("devices", "drive-removable-media"),
    "katu-trash-empty.png":     ("places",  "user-trash"),
    "katu-trash-full.png":      ("places",  "user-trash-full"),
    "katu-usb.png":             ("devices", "drive-removable-media-usb"),
}

for sz in [256, 128, 64, 48]:
    for src_name, (cat, std_name) in SYSTEM_ICONS.items():
        src = pack("plasma", "icons", src_name)
        # Into katu theme
        process(src, KATU_THEME / f"{sz}x{sz}/{cat}/{std_name}.png", (sz, sz))
        # Into hicolor as fallback (standard names)
        process(src, INC / f"usr/share/icons/hicolor/{sz}x{sz}/{cat}/{std_name}.png", (sz, sz))

# Copy all app icons into katu theme too (so kickoff menu uses them)
for sz in [256, 128, 64, 48]:
    for name, src in ICON_SOURCES.items():
        process(src, KATU_THEME / f"{sz}x{sz}/apps/{name}.png", (sz, sz))

# katu theme index.theme (inherits breeze-dark for everything else)
SIZES = "256x256,128x128,64x64,48x48"
dirs_apps  = ",".join(f"{s}/apps"    for s in SIZES.split(","))
dirs_place = ",".join(f"{s}/places"  for s in SIZES.split(","))
dirs_dev   = ",".join(f"{s}/devices" for s in SIZES.split(","))

INDEX = f"""\
[Icon Theme]
Name=Katu
Comment=Katu OS Icon Theme — Amazônia style
Inherits=breeze-dark,hicolor
Directories={dirs_apps},{dirs_place},{dirs_dev}

"""
for sz in SIZES.split(","):
    n = sz.split("x")[0]
    for cat, ctx in [("apps","Applications"), ("places","Places"), ("devices","Devices")]:
        INDEX += f"[{sz}/{cat}]\nSize={n}\nContext={ctx}\nType=Fixed\n\n"

index_path = KATU_THEME / "index.theme"
index_path.parent.mkdir(parents=True, exist_ok=True)
index_path.write_text(INDEX)
print(f"  ✓  katu/index.theme written")

# ─────────────────────────────────────────────────────────────────────────────
# 7. CALAMARES BRANDING  logo + icon + welcome + 6 slides
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 7. Calamares branding ──")

CAL = INC / "etc/calamares/branding/katu"

# Product logo (shown in wizard header bar): wide horizontal logo
process(site("logo-horizontal-wide.png"), CAL / "logo.png", (300, 120))
# Product icon (shown in taskbar / About): circular jaguar icon
process(img("17_41_29"), CAL / "icon.png", (96, 96))
# Welcome background (right panel of Bem-vindo step)
process(img("17_12_03"), CAL / "welcome.png", (1024, 576))

# 6 installation slides from the final-assets pack
for i in range(1, 7):
    fname = f"slide-{i:02d}.png"
    copy(pack("installer", "calamares", "slides", fname), CAL / fname)

# ─────────────────────────────────────────────────────────────────────────────
# 8. LIVE WELCOME IMAGE  + branding assets
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 8. Live welcome + branding ──")

BRAND = INC / "usr/share/katu/branding"

copy(pack("installer", "live", "katu-live-welcome.png"), BRAND / "katu-live-welcome.png")

LOGO_VARIANTS = {
    "katu-logo-dark.png":       pack("branding", "logo", "katu-os-dark.png"),
    "katu-logo-white.png":      pack("branding", "logo", "katu-os-white.png"),
    "katu-logo-mono.png":       pack("branding", "logo", "katu-os-monochrome.png"),
    "katu-symbol-white.png":    pack("branding", "logo", "katu-symbol-white.png"),
    "katu-symbol-mono.png":     pack("branding", "logo", "katu-symbol-monochrome.png"),
    "katu-logo-horizontal.png": site("logo-horizontal-wide.png"),
    "katu-emblema.png":         site("emblema-onca.png"),
    "hero-onca-amazonia.png":   site("hero-onca-amazonia.png"),
}
for name, src in LOGO_VARIANTS.items():
    copy(src, BRAND / name)

print("\n✅  All Katu OS assets applied successfully.\n")
