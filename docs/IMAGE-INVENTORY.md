# Katu OS — Inventário de Imagens Oficiais

> Fonte: `C:\katuos\imagens\katu-os-final-assets\`  
> Gerado em: 2026-09-25

---

## Wallpapers (6 imagens)

| Arquivo | Resolução | Proporção | Alpha | Formato | Tamanho | Uso | Destino |
|---------|-----------|-----------|-------|---------|---------|-----|---------|
| `wallpapers/katu-amazonia-4k.png` | 3840×2160 | 16:9 | Não | RGB PNG | 103,645 B | Wallpaper principal | `usr/share/wallpapers/katu/contents/images/` |
| `wallpapers/katu-onca-4k.png` | 3840×2160 | 16:9 | Não | RGB PNG | 100,016 B | Wallpaper Onça | `usr/share/wallpapers/katu/contents/images/` |
| `wallpapers/katu-dark-4k.png` | 3840×2160 | 16:9 | Não | RGB PNG | 103,721 B | Wallpaper Dark | `usr/share/wallpapers/katu/contents/images/` |
| `wallpapers/katu-green-4k.png` | 3840×2160 | 16:9 | Não | RGB PNG | 101,842 B | Wallpaper Light | `usr/share/wallpapers/katu/contents/images/` |
| `wallpapers/katu-minimal-4k.png` | 3840×2160 | 16:9 | Não | RGB PNG | 102,887 B | Wallpaper Minimal | `usr/share/wallpapers/katu/contents/images/` |
| `wallpapers/katu-rio-4k.png` | 3840×2160 | 16:9 | Não | RGB PNG | 94,976 B | Wallpaper Rio | `usr/share/wallpapers/katu/contents/images/` |

---

## Logos e Símbolos (5 imagens)

| Arquivo | Resolução | Proporção | Alpha | Formato | Tamanho | Uso | Destino |
|---------|-----------|-----------|-------|---------|---------|-----|---------|
| `branding/logo/katu-os-dark.png` | 1800×600 | 3:1 | Sim | RGBA PNG | 35,607 B | Logo horizontal escuro | `usr/share/katu/branding/logos/` |
| `branding/logo/katu-os-white.png` | 1800×600 | 3:1 | Sim | RGBA PNG | 29,731 B | Logo horizontal branco | `usr/share/katu/branding/logos/`, SDDM, Calamares, pixmaps (derivado) |
| `branding/logo/katu-os-monochrome.png` | 1800×600 | 3:1 | Sim | RGBA PNG | 29,353 B | Logo horizontal mono | `usr/share/katu/branding/logos/` |
| `branding/logo/katu-symbol-white.png` | 1024×1024 | 1:1 | Sim | RGBA PNG | 16,539 B | Símbolo quadrado branco | Calamares icon, app icons |
| `branding/logo/katu-symbol-monochrome.png` | 1024×1024 | 1:1 | Sim | RGBA PNG | 16,539 B | Símbolo quadrado mono | `usr/share/katu/branding/logos/` |

---

## Plymouth (4 imagens)

| Arquivo | Resolução | Alpha | Tamanho | Uso | Destino |
|---------|-----------|-------|---------|-----|---------|
| `plymouth/katu/katu-logo-boot-light.png` | 1024×1024 | Sim | 21,315 B | Logo original (fonte) — usada também como katu-logo.png base | `plymouth/themes/katu/` (derivada 300×300) |
| `plymouth/katu/spinner.png` | 512×512 | Sim | 8,188 B | Animação de carregamento (imagem única) | `plymouth/themes/katu/spinner.png` |
| `plymouth/katu/progress-dot.png` | 128×128 | Sim | 836 B | Ponto de progresso | `plymouth/themes/katu/progress-dot.png` |

> **Nota spinner:** o `katu.script` não realiza animação por frame — o spinner é exibido como imagem estática. O campo `frames=8` é vestigial no script atual.

---

## GRUB (2 imagens)

| Arquivo | Resolução | Alpha | Tamanho | Uso | Destino |
|---------|-----------|-------|---------|-----|---------|
| `grub/katu-grub-logo.png` | 1000×320 | Sim | 14,179 B | Logo no menu de boot | `boot/grub/themes/katu/katu-grub-logo.png` |
| `grub/katu-selection.png` | 1400×120 | Sim | 1,428 B | Indicador de seleção | `boot/grub/themes/katu/katu-selection.png` |

> **Nota:** o `theme.txt` usa `selected_item_pixmap_style = "select_bkg_*.png"` — se esses sprites não existirem, o GRUB usa cor de fallback. A ISO atual funciona sem eles.

---

## Calamares (10 imagens)

| Arquivo | Resolução | Alpha | Tamanho | Uso | Destino |
|---------|-----------|-------|---------|-----|---------|
| `installer/live/katu-live-welcome.png` | 1920×1080 | Não | 61,830 B | Tela de boas-vindas do instalador | `calamares/branding/katu/welcome.png` |
| `installer/calamares/slides/slide-01.png` | 1920×1080 | Não | 55,389 B | Slide 1: Bem-vindo | `calamares/branding/katu/slide-01.png` |
| `installer/calamares/slides/slide-02.png` | 1920×1080 | Não | 51,142 B | Slide 2: Simples e fácil | `calamares/branding/katu/slide-02.png` |
| `installer/calamares/slides/slide-03.png` | 1920×1080 | Não | 55,954 B | Slide 3: Apps essenciais | `calamares/branding/katu/slide-03.png` |
| `installer/calamares/slides/slide-04.png` | 1920×1080 | Não | 55,329 B | Slide 4: Seguro | `calamares/branding/katu/slide-04.png` |
| `installer/calamares/slides/slide-05.png` | 1920×1080 | Não | 53,563 B | Slide 5: Brasil no DNA | `calamares/branding/katu/slide-05.png` |
| `installer/calamares/slides/slide-06.png` | 1920×1080 | Não | 52,650 B | Slide 6: Software livre | `calamares/branding/katu/slide-06.png` |

---

## Ícones de Aplicativos (4 imagens oficiais)

| Arquivo | Resolução | Alpha | Tamanho | App | Destino |
|---------|-----------|-------|---------|-----|---------|
| `applications/katu-backup.png` | 1024×1024 | Não | 21,679 B | Backup | `icons/hicolor/256x256/apps/` |
| `applications/katu-feedback.png` | 1024×1024 | Não | 21,237 B | Feedback | `icons/hicolor/256x256/apps/` |
| `applications/katu-security.png` | 1024×1024 | Não | 22,963 B | Security | `icons/hicolor/256x256/apps/` |
| `applications/katu-system-info.png` | 1024×1024 | Não | 23,445 B | System Info | `icons/hicolor/256x256/apps/` |

---

## Ícones de Places/Devices (7 imagens)

| Arquivo | Resolução | Alpha | Tamanho | Ícone |
|---------|-----------|-------|---------|-------|
| `plasma/icons/katu-computer.png` | 1024×1024 | Não | 16,203 B | Computador |
| `plasma/icons/katu-home.png` | 1024×1024 | Não | 16,748 B | Pasta Pessoal |
| `plasma/icons/katu-network.png` | 1024×1024 | Não | 17,700 B | Rede |
| `plasma/icons/katu-removable-drive.png` | 1024×1024 | Não | 17,248 B | Drive removível |
| `plasma/icons/katu-trash-empty.png` | 1024×1024 | Não | 15,833 B | Lixeira vazia |
| `plasma/icons/katu-trash-full.png` | 1024×1024 | Não | 15,948 B | Lixeira cheia |
| `plasma/icons/katu-usb.png` | 1024×1024 | Não | 16,711 B | USB |

---

## Cursor (referência, não funcional como tema XCursor)

| Arquivo | Resolução | Alpha | Tamanho | Observação |
|---------|-----------|-------|---------|------------|
| `plasma/cursors/katu-cursor-master.png` | 2048×2048 | Não | 78,477 B | Matriz visual — requer conversão para tema XCursor funcional |

> **Decisão:** cursor não foi implementado como tema XCursor nesta versão para não comprometer funcionalidade. O cursor Breeze padrão permanece ativo.

---

## Assets Derivados (gerados em `build/generated-assets/`)

| Arquivo gerado | Fonte | Resolução | Destino principal |
|----------------|-------|-----------|-------------------|
| `grub/background.png` | `katu-amazonia-4k.png` | 1920×1080 | GRUB background (3 dirs) |
| `plymouth/logo.png` | `katu-logo-boot-light.png` | 300×300 | Plymouth boot logo |
| `sddm/background.png` | `katu-amazonia-4k.png` | 1920×1080 | SDDM login background |
| `sddm/logo.png` | `katu-os-white.png` | 330×110 | SDDM logo (QML: 110×44) |
| `pixmaps/katu-logo.png` | `katu-os-white.png` | 360×120 | Splash KDE (QML: 180×72) |
| `calamares/logo.png` | `katu-os-white.png` | 400×133 | Calamares sidebar logo |
| `calamares/icon.png` | `katu-symbol-white.png` | 64×64 | Calamares window icon |
