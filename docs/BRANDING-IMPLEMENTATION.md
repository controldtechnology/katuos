# Katu OS — Branding Implementation Report

> Data: 2026-09-25  
> Branch: `visual/katu-brand-identity`  
> Script: `scripts/sync-katu-assets.sh`  
> Validator: `scripts/validate-branding.sh`

---

## Status de Implementação

| Área | Status | Notas |
|------|--------|-------|
| [x] GRUB background | **OK** | 1920×1080 derivado de `katu-amazonia-4k.png` |
| [x] GRUB logo | **OK** | `katu-grub-logo.png` 1000×320 RGBA |
| [x] GRUB selection | **OK** | `katu-selection.png` 1400×120 RGBA |
| [x] Plymouth logo | **OK** | `katu-logo-boot-light.png` redimensionada 300×300 |
| [x] Plymouth spinner | **OK** | `spinner.png` 512×512 RGBA (imagem estática) |
| [x] Plymouth progress-dot | **OK** | `progress-dot.png` 128×128 RGBA |
| [x] SDDM background | **OK** | 1920×1080 derivado de `katu-amazonia-4k.png` |
| [x] SDDM logo | **OK** | `katu-os-white.png` 330×110 (3:1 → QML: 110×44) |
| [x] KDE Splash pixmaps | **OK** | `katu-os-white.png` 360×120 (QML usa 180×72) |
| [x] Wallpaper Amazônia (padrão) | **OK** | 3840×2160 original |
| [x] Wallpaper Onça | **OK** | 3840×2160 original |
| [x] Wallpaper Dark | **OK** | 3840×2160 original |
| [x] Wallpaper Light | **OK** | 3840×2160 original |
| [x] Wallpaper Minimal | **OK** | 3840×2160 original |
| [x] Wallpaper Rio | **OK** | 3840×2160 original |
| [x] Calamares logo | **OK** | `katu-os-white.png` 400×133 |
| [x] Calamares icon | **OK** | `katu-symbol-white.png` 64×64 |
| [x] Calamares welcome | **OK** | `katu-live-welcome.png` 1920×1080 |
| [x] Calamares slide-01 | **OK** | `slide-01.png` 1920×1080 |
| [x] Calamares slide-02 | **OK** | `slide-02.png` 1920×1080 |
| [x] Calamares slide-03 | **OK** | `slide-03.png` 1920×1080 |
| [x] Calamares slide-04 | **OK** | `slide-04.png` 1920×1080 |
| [x] Calamares slide-05 | **OK** | `slide-05.png` 1920×1080 |
| [x] Calamares slide-06 | **OK** | `slide-06.png` 1920×1080 |
| [x] App icons 256×256 (17) | **OK** | Fontes dedicadas para 4; símbolo Katu para os demais |
| [x] katu-logo hicolor (4 tamanhos) | **OK** | 256, 128, 64, 48 |
| [x] Theme icons katu (7 ícones × 2 sizes) | **OK** | 64×64 e 32×32 |
| [x] Logos oficiais branding | **OK** | 5 arquivos sincronizados |
| [x] About Distro (kcm-about-distro.conf) | **OK** | LogoPath aponta para pixmaps correto |
| [x] Live installer desktop | **OK** | .desktop files verificados |
| [x] Look-and-feel wallpaper default | **OK** | `katu-amazonia-4k.png` em `contents/defaults` |

---

## Correções Críticas Aplicadas

### 1. Plymouth logo (CRÍTICO)
- **Antes:** `1254×1254` RGBA (ChatGPT) — preencheria a tela inteira  
- **Depois:** `300×300` RGBA derivada do logo oficial  
- **Impacto:** animação de boot ficará correta no ecrã

### 2. pixmaps/katu-logo.png (CRÍTICO)
- **Antes:** `1254×1254` RGBA  
- **Depois:** `360×120` RGBA (horizontal logo, QML renderiza em 180×72)  
- **Impacto:** Splash KDE e About Distro corretos

### 3. Ícones hicolor 256×256 (CRÍTICO)
- **Antes:** todos em `1254×1254` (dimensão errada, categoria errada)  
- **Depois:** todos em `256×256` exatos  
- **Impacto:** ícones de apps corretos no menu e taskbar

### 4. SDDM/GRUB background (VISUAL)
- **Antes:** `1672×941` (imagem ChatGPT provisória)  
- **Depois:** `1920×1080` HD derivado de `katu-amazonia-4k.png`  
- **Impacto:** tela de login e boot em alta definição

### 5. SDDM logo (VISUAL)
- **Antes:** `1024×1024` (símbolo quadrado — exibia como 44×44 deformado)  
- **Depois:** `330×110` (logo horizontal — preenche corretamente 110×44 no QML)  
- **Impacto:** logo legível na tela de login

---

## O que NÃO foi alterado (funcionalidade preservada)

- `katu.plymouth` — manifesto Plymouth
- `katu.script` — lógica de animação Plymouth
- `theme.txt` — layout GRUB
- `Main.qml` — layout SDDM e autenticação
- `Splash.qml` — animação splash KDE
- `show.qml` — slideshow Calamares
- `branding.desc` — configuração Calamares
- `kdeglobals` — configuração KDE
- Todos os hooks de build
- Configuração funcional do Calamares (módulos, particionamento, etc.)
- Kernel, initramfs, systemd, drivers, rede

---

## Validação

```
python3 scripts/validate-branding.sh
```

**Resultado:** 85 OK, 0 ERRORS, 0 WARNINGS

---

## Assets gerados em `build/generated-assets/`

| Arquivo | Fonte | Resolução |
|---------|-------|-----------|
| `grub/background.png` | `katu-amazonia-4k.png` | 1920×1080 |
| `plymouth/logo.png` | `katu-logo-boot-light.png` | 300×300 |
| `sddm/background.png` | `katu-amazonia-4k.png` | 1920×1080 |
| `sddm/logo.png` | `katu-os-white.png` | 330×110 |
| `pixmaps/katu-logo.png` | `katu-os-white.png` | 360×120 |
| `calamares/logo.png` | `katu-os-white.png` | 400×133 |
| `calamares/icon.png` | `katu-symbol-white.png` | 64×64 |
| `MANIFEST.json` | — | — |

---

## Próximos passos

1. Commit de todos os changes no branch `visual/katu-brand-identity`
2. Build da nova ISO via WSL2: `sudo bash scripts/build-clean.sh`
3. Nova ISO em: `output/katu-os-<VERSION>-<TIMESTAMP>-amd64.iso`
4. Testes: GRUB → Plymouth → Live → Calamares → Instalação → SDDM → Desktop
5. Gerar `VISUAL-REBRANDING-REPORT.md` após testes

---

## Notas de decisão

**Cursor:** O arquivo `plasma/cursors/katu-cursor-master.png` (2048×2048) é uma matriz visual, não um tema XCursor funcional. Implementar um tema XCursor requer uma ferramenta como `xcursorgen` e seria uma alteração técnica que vai além do visual puro. Decisão: manter cursor Breeze padrão para não comprometer usabilidade.

**Ícones sem fonte dedicada:** Para apps sem ícone oficial (browser, terminal, etc.), foi utilizado o símbolo oficial `katu-symbol-white.png`. Esta é a abordagem mais consistente com a identidade — todo app Katu exibe o símbolo da marca até que ícones dedicados sejam criados.
