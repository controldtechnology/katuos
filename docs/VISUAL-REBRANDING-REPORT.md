# Katu OS — Visual Rebranding Report

> Data: 2026-09-25  
> Branch: `visual/katu-brand-identity`  
> Commit: `e8b0215`  
> Executado por: sync-katu-assets.sh + validate-branding.sh

---

## Baseline

| Campo | Valor |
|-------|-------|
| ISO original (dist/) | `KatuOS-Premium-1.0.1-rc1-66973a00-x86_64.iso` |
| SHA256 | `a86d37563af171dc83a0bebdcd6653714f71fc432e3e497186a760ffd9bded2d` |
| Tamanho | 3.23 GB |
| Status | **PRESERVADA — não alterada** |
| ISO candidata (output/) | `katu-os-1.0.1-rc1-amd64.iso` |
| SHA256 candidata | `6d992b91b5978a4cd61d8bf82942405f577ca0501409c784755c46fccfea6dfd` |
| Tag git de checkpoint | `baseline/pre-rebranding-visual-v2-20260925` |

---

## Assets

| Campo | Valor |
|-------|-------|
| Fonte | `C:\katuos\imagens\katu-os-final-assets\` |
| Total de assets na fonte | 35 imagens |
| Total de operações executadas | 118 (cópias + derivações) |
| Total de destinos atualizados | 77 arquivos no repositório |
| Erros | 0 |
| Derivados gerados | 7 em `build/generated-assets/` |

---

## GRUB

| Item | Status | Detalhes |
|------|--------|---------|
| background.png | **OK** | 1920×1080 derivado de `katu-amazonia-4k.png` |
| katu-grub-logo.png | **OK** | 1000×320 RGBA oficial |
| katu-selection.png | **OK** | 1400×120 RGBA oficial |
| theme.txt | **Preservado** | Layout não alterado |
| Entradas de boot | **Preservadas** | Nenhum parâmetro alterado |

---

## Plymouth

| Item | Status | Detalhes |
|------|--------|---------|
| logo.png | **OK** | Corrigido: 1254×1254 → **300×300** (escala correta) |
| katu-logo-boot-light.png | **OK** | 1024×1024 RGBA original preservado |
| spinner.png | **OK** | 512×512 RGBA (imagem estática funcional) |
| progress-dot.png | **OK** | 128×128 RGBA |
| katu.script | **Preservado** | Lógica de animação não alterada |
| katu.plymouth | **Preservado** | Manifesto não alterado |

---

## SDDM

| Item | Status | Detalhes |
|------|--------|---------|
| background.png | **OK** | Corrigido: 1672×941 ChatGPT → **1920×1080** |
| logo.png | **OK** | Corrigido: símbolo 1024×1024 → **logo horizontal 330×110** |
| Main.qml | **Preservado** | Layout e autenticação não alterados |
| theme.conf | **Preservado** | Configuração não alterada |

---

## Plasma / KDE Splash

| Item | Status | Detalhes |
|------|--------|---------|
| pixmaps/katu-logo.png | **OK** | Corrigido: 1254×1254 → **360×120** (QML usa 180×72) |
| Splash.qml | **Preservado** | Animação não alterada |
| Look-and-feel defaults | **Verificado** | Aponta para `katu-amazonia-4k.png` ✓ |
| kcm-about-distro.conf | **Verificado** | `LogoPath` correto ✓ |

---

## Wallpapers

| Item | Status | Resolução |
|------|--------|-----------|
| katu-amazonia-4k.png **(padrão)** | **OK** | 3840×2160 |
| katu-onca-4k.png | **OK** | 3840×2160 |
| katu-dark-4k.png | **OK** | 3840×2160 |
| katu-green-4k.png | **OK** | 3840×2160 |
| katu-minimal-4k.png | **OK** | 3840×2160 |
| katu-rio-4k.png | **OK** | 3840×2160 |

---

## Calamares

| Item | Status | Detalhes |
|------|--------|---------|
| logo.png | **OK** | 400×133 (`katu-os-white.png` derivado) |
| icon.png | **OK** | 64×64 (`katu-symbol-white.png` derivado) |
| welcome.png | **OK** | 1920×1080 (`katu-live-welcome.png` original) |
| slide-01 a slide-06 | **OK** | 6× 1920×1080 |
| branding.desc | **Preservado** | Configuração funcional não alterada |
| show.qml | **Preservado** | Slideshow (7s/slide) não alterado |
| Módulos (partição, users, etc.) | **Preservados** | Nenhuma lógica alterada |

---

## Ícones

| Grupo | Status | Detalhes |
|-------|--------|---------|
| hicolor 256×256 (17 ícones) | **OK** | Todos corrigidos de 1254×1254 → 256×256 |
| hicolor katu-logo (4 tamanhos) | **OK** | 256, 128, 64, 48 |
| katu theme 64×64 (7 ícones) | **OK** | Rescalado de 1024→64 |
| katu theme 32×32 (7 ícones) | **OK** | Rescalado de 1024→32 |

---

## Live Mode

| Item | Status |
|------|--------|
| Wallpaper default | katu-amazonia-4k via look-and-feel ✓ |
| Tema Katu | org.katuos.desktop ✓ |
| Logo Splash | 360×120 horizontal (era 1254×1254) ✓ |
| Ícones apps | 256×256 corretos ✓ |
| Atalho instalador | katu-install.desktop ✓ |

---

## Validação de Assets

```
python3 scripts/validate-branding.sh
```

**Resultado final:** 105 OK · 0 WARNINGS · 0 ERRORS

---

## Build da Nova ISO

O build requer **Linux como root** (WSL2 ou máquina Linux).

### Via WSL2 (Windows)

```powershell
# No PowerShell como Administrador:
wsl -d Debian -- bash -c "cd /mnt/c/katuos && sudo bash scripts/build-clean.sh"
```

### Via Linux direto

```bash
cd /path/to/katuos
sudo bash scripts/build-clean.sh
```

A nova ISO será gerada em:
```
output/katu-os-1.0.1-rc1-<TIMESTAMP>-<COMMIT>-amd64.iso
```

**Verificar que o nome é DIFERENTE das ISOs anteriores antes de qualquer limpeza.**

---

## Checklist de Testes (pós-build)

```
[ ] ISO original preservada (SHA256 verificado)
[ ] Nova ISO criada com nome diferente
[ ] SHA256 gerado para nova ISO
[ ] GRUB aparece — tema Katu (fundo Amazônia)
[ ] Plymouth aparece — logo 300x300 centralizado
[ ] Live Mode carrega
[ ] Wallpaper katu-amazonia aparece no desktop
[ ] Painel KDE funciona
[ ] Menu KDE funciona
[ ] Ícones de apps visíveis (256x256 corretos)
[ ] Dolphin abre — ícones de places corretos
[ ] Calamares abre — logo e welcome corretos
[ ] Slides do instalador aparecem durante instalação
[ ] Instalação completa conclui
[ ] Reboot após instalação
[ ] SDDM aparece — fundo 1920x1080 + logo horizontal
[ ] Login funciona
[ ] Desktop instalado carrega com tema Katu
[ ] Nenhuma regressão funcional
```

---

## Regressões Conhecidas

Nenhuma esperada — apenas assets visuais foram alterados.  
A funcionalidade (boot, instalação, login, rede) não foi tocada.

---

## Problemas Conhecidos / Não Implementados

| Item | Razão |
|------|-------|
| Cursor Katu XCursor | `katu-cursor-master.png` é matriz visual — requer `xcursorgen` para converter; alteração técnica fora do escopo visual puro |
| Ícones sem fonte dedicada usam símbolo | Apenas 4 apps têm ícones oficiais no pack; símbolo Katu é a escolha mais consistente |
| Widgets de sistema (clima, CPU) | Dependem de configuração do usuário; não foram hardcoded |

---

## Git

| Campo | Valor |
|-------|-------|
| Branch | `visual/katu-brand-identity` |
| Commit rebranding | `e8b0215` |
| Tag checkpoint | `baseline/pre-rebranding-visual-v2-20260925` |
| Arquivos alterados | 77 |
| Inserções | 1,533+ |
