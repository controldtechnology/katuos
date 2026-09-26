# Katu OS — Auditoria Completa de Imagens e Ícones

> Gerado em: 2026-09-25  
> Branch: `visual/katu-brand-identity`  
> Escopo: todos os pontos do sistema onde imagens e ícones podem ser trocados

---

## Sumário

| # | Área | Arquivos | Caminho principal |
|---|------|----------|-------------------|
| 1 | Boot — GRUB | 3 imagens | `config/includes.binary/boot/grub/themes/katu/` |
| 2 | Boot — Plymouth (splash de boot) | 4 imagens | `config/includes.chroot/usr/share/plymouth/themes/katu/` |
| 3 | Login — SDDM | 2 imagens | `config/includes.chroot/usr/share/sddm/themes/katu/` |
| 4 | Splash do KDE (carregamento da sessão) | 1 imagem via código | `config/includes.chroot/usr/share/plasma/look-and-feel/org.katuos.desktop/` |
| 5 | Área de trabalho — Wallpapers | 6 imagens | `config/includes.chroot/usr/share/wallpapers/katu/contents/images/` |
| 6 | Instalador Calamares — branding | 9 imagens | `config/includes.chroot/etc/calamares/branding/katu/` |
| 7 | Instalador Calamares — slides | 6 imagens | `config/includes.chroot/etc/calamares/branding/katu/slide-*.png` |
| 8 | Ícones de apps Katu (hicolor) | 17 ícones | `config/includes.chroot/usr/share/icons/hicolor/` |
| 9 | Ícones do tema Katu (places/devices) | 14 ícones | `config/includes.chroot/usr/share/icons/katu/` |
| 10 | Logo global do sistema (pixmaps) | 1 imagem | `config/includes.chroot/usr/share/pixmaps/` |
| 11 | Logos da marca Katu (branding oficial) | 5 logos | `config/includes.chroot/usr/share/katu/branding/logos/` |
| 12 | Sobre o sistema (KDE About) | 1 imagem via conf | `config/includes.chroot/etc/xdg/kcm-about-distro.conf` |
| 13 | Desktop Live — atalho instalador | ícone via .desktop | `config/includes.chroot/etc/skel/Área de Trabalho/` |
| 14 | Repositório de fonte / branding externo | variados | `branding/` e `imagens/` |

---

## 1. GRUB — Tela de boot

**Onde aparece:** tela de seleção de sistema operacional antes do kernel carregar.

### Arquivos de imagem

| Arquivo | Função | Formato recomendado |
|---------|--------|---------------------|
| `background.png` | Fundo da tela inteira do GRUB | PNG, qualquer resolução (1920×1080 ideal) |
| `katu-grub-logo.png` | Logo exibida no canto/área central | PNG com transparência |
| `katu-selection.png` | Indicador visual do item selecionado no menu | PNG, sprite estilo `select_bkg_*.png` |

### Caminhos no repo

```
config/includes.binary/boot/grub/themes/katu/background.png
config/includes.binary/boot/grub/themes/katu/katu-grub-logo.png
config/includes.binary/boot/grub/themes/katu/katu-selection.png

config/includes.chroot/boot/grub/themes/katu/background.png     ← cópia para o chroot
config/includes.chroot/boot/grub/themes/katu/katu-grub-logo.png
config/includes.chroot/boot/grub/themes/katu/katu-selection.png
```

### Arquivo de tema (layout / referências)

```
config/includes.binary/boot/grub/themes/katu/theme.txt
config/includes.chroot/boot/grub/themes/katu/theme.txt
```

> **Nota:** A propriedade `desktop-image` neste arquivo aponta para `background.png`.  
> O estilo `selected_item_pixmap_style = "select_bkg_*.png"` espera sprites com esse padrão de nome.

---

## 2. Plymouth — Splash de inicialização do kernel

**Onde aparece:** animação exibida enquanto o kernel e os serviços do Linux sobem (antes do SDDM).

### Arquivos de imagem

| Arquivo | Função |
|---------|--------|
| `logo.png` | Logo central animada com fade-in |
| `katu-logo-boot-light.png` | Variante clara (uso alternativo no script) |
| `spinner.png` | Sprite sheet do spinner (8 frames, lidos sequencialmente) |
| `progress-dot.png` | Ponto individual da barra de progresso |

### Caminhos no repo

```
config/includes.chroot/usr/share/plymouth/themes/katu/logo.png
config/includes.chroot/usr/share/plymouth/themes/katu/katu-logo-boot-light.png
config/includes.chroot/usr/share/plymouth/themes/katu/spinner.png
config/includes.chroot/usr/share/plymouth/themes/katu/progress-dot.png
```

### Arquivos de controle

```
config/includes.chroot/usr/share/plymouth/themes/katu/katu.plymouth   ← manifesto do tema
config/includes.chroot/usr/share/plymouth/themes/katu/katu.script      ← lógica da animação
```

> **Nota sobre o spinner:** o script lê `spinner.png` como sprite sheet com `frames = 8`.  
> A imagem deve conter 8 frames horizontais, cada um com a mesma largura.

---

## 3. SDDM — Tela de login

**Onde aparece:** tela de autenticação antes de entrar na sessão KDE.

### Arquivos de imagem

| Arquivo | Função | Referência no código |
|---------|--------|---------------------|
| `background.png` | Wallpaper de fundo da tela de login | `theme.conf → background=background.png` e `Main.qml → config.background \|\| "background.png"` |
| `logo.png` | Logo no canto inferior esquerdo | `Main.qml → source: "logo.png"` |

### Caminhos no repo

```
config/includes.chroot/usr/share/sddm/themes/katu/background.png
config/includes.chroot/usr/share/sddm/themes/katu/logo.png
```

### Arquivos de controle

```
config/includes.chroot/usr/share/sddm/themes/katu/theme.conf      ← define background e cor de fallback
config/includes.chroot/usr/share/sddm/themes/katu/Main.qml        ← layout completo da tela de login
config/includes.chroot/usr/share/sddm/themes/katu/metadata.desktop
```

> **Dimensões sugeridas:** `background.png` deve ser no mínimo 1920×1080; o QML usa `PreserveAspectCrop`.  
> `logo.png` é exibida com `width: 110, height: 44` — proporcional horizontal (ex.: 220×88 ou 440×176).

---

## 4. Splash KDE Plasma — Carregamento da sessão

**Onde aparece:** logo após o login, enquanto o ambiente KDE carrega (antes do desktop aparecer).

### Imagem referenciada

| Arquivo | Onde está | Como é usado |
|---------|-----------|--------------|
| `katu-logo.png` (48px) | `/usr/share/pixmaps/katu-logo.png` | Referenciado diretamente no QML via path absoluto |

### Caminho do QML

```
config/includes.chroot/usr/share/plasma/look-and-feel/org.katuos.desktop/contents/splash/Splash.qml
config/includes.chroot/etc/katuos-looknfeel/contents/splash/Splash.qml  ← cópia em /etc
```

> **Para trocar:** altere a linha `source: "/usr/share/pixmaps/katu-logo.png"` no `Splash.qml`  
> e/ou substitua o arquivo em `config/includes.chroot/usr/share/pixmaps/katu-logo.png`.  
> Dimensão no QML: `width: 180, height: 72`.

---

## 5. Área de trabalho — Wallpapers

**Onde aparece:** papel de parede padrão do desktop KDE.

### Imagens

| Arquivo | Nome exibido | Padrão? |
|---------|-------------|---------|
| `katu-amazonia-4k.png` | Katu Amazon | **sim** |
| `katu-onca-4k.png` | Katu Jaguar | não |
| `katu-dark-4k.png` | Katu Dark | não |
| `katu-green-4k.png` | Katu Light | não |
| `katu-minimal-4k.png` | Katu Minimal | não |
| `katu-rio-4k.png` | Katu River | não |

### Caminhos no repo

```
config/includes.chroot/usr/share/wallpapers/katu/contents/images/katu-amazonia-4k.png
config/includes.chroot/usr/share/wallpapers/katu/contents/images/katu-onca-4k.png
config/includes.chroot/usr/share/wallpapers/katu/contents/images/katu-dark-4k.png
config/includes.chroot/usr/share/wallpapers/katu/contents/images/katu-green-4k.png
config/includes.chroot/usr/share/wallpapers/katu/contents/images/katu-minimal-4k.png
config/includes.chroot/usr/share/wallpapers/katu/contents/images/katu-rio-4k.png
```

### Arquivos de controle

```
config/includes.chroot/usr/share/wallpapers/katu/metadata.json   ← registro de cada wallpaper
config/includes.chroot/etc/xdg/kdeglobals                        ← define wallpaper padrão (linha [Wallpaper] Image=...)
```

> **Para adicionar um wallpaper:** coloque o arquivo em `contents/images/` e registre no `metadata.json`.  
> **Para trocar o padrão:** edite `[Wallpaper] Image=` no `kdeglobals`.

---

## 6. Instalador Calamares — Branding geral

**Onde aparece:** janela do instalador Calamares (logo, ícone da janela, imagem de boas-vindas).

### Arquivos de imagem

| Arquivo | Função | Tamanho típico |
|---------|--------|----------------|
| `logo.png` | Logo no painel lateral do instalador | 200×80 px |
| `icon.png` | Ícone da janela do instalador (barra de título, taskbar) | 64×64 px |
| `welcome.png` | Imagem de boas-vindas (primeira tela do wizard) | 800×400 px |

### Caminhos no repo

```
config/includes.chroot/etc/calamares/branding/katu/logo.png
config/includes.chroot/etc/calamares/branding/katu/icon.png
config/includes.chroot/etc/calamares/branding/katu/welcome.png

installer/calamares/branding/katu/logo.png     ← cópia/fonte
installer/calamares/branding/katu/icon.png
installer/calamares/branding/katu/welcome.png
```

### Arquivo de controle

```
config/includes.chroot/etc/calamares/branding/katu/branding.desc
installer/calamares/branding/katu/branding.desc
```

> As chaves relevantes em `branding.desc`:
> ```yaml
> images:
>     productLogo:    "logo.png"
>     productIcon:    "icon.png"
>     productWelcome: "welcome.png"
> ```

---

## 7. Instalador Calamares — Slides (durante instalação)

**Onde aparece:** slideshow exibido enquanto os arquivos são copiados para o disco.

### Arquivos de imagem

| Arquivo | Slide | Título |
|---------|-------|--------|
| `slide-01.png` | 1/6 | Bem-vindo ao Katu OS! |
| `slide-02.png` | 2/6 | Simples e fácil |
| `slide-03.png` | 3/6 | Aplicativos essenciais |
| `slide-04.png` | 4/6 | Seguro e atualizado |
| `slide-05.png` | 5/6 | Brasil no nosso DNA |
| `slide-06.png` | 6/6 | Software livre |

### Caminhos no repo

```
config/includes.chroot/etc/calamares/branding/katu/slide-01.png
...
config/includes.chroot/etc/calamares/branding/katu/slide-06.png

installer/calamares/branding/katu/slide-01.png   ← cópias/fonte
...
installer/calamares/branding/katu/slide-06.png
```

### Arquivo de controle do slideshow

```
config/includes.chroot/etc/calamares/branding/katu/show.qml
installer/calamares/branding/katu/show.qml
```

> O QML usa `Image { source: modelData.img }` apontando para cada slide.  
> Para adicionar slides: inclua na lista `slideData` em `show.qml` e adicione os arquivos PNG.  
> Auto-avanço configurado em `Timer { interval: 7000 }` (7 segundos por slide).

---

## 8. Ícones de aplicativos Katu — hicolor

**Onde aparecem:** menu de aplicativos, taskbar, gerenciador de arquivos — ícones dos apps proprietários do Katu.

### Ícones em 256×256

```
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-backup.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-browser.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-connect.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-drivers.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-feedback.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-files.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-help.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-home.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-installer.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-logo.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-security.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-settings.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-store.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-system-info.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-terminal.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-user.png
config/includes.chroot/usr/share/icons/hicolor/256x256/apps/katu-welcome.png
```

### Ícones em outros tamanhos (katu-logo)

```
config/includes.chroot/usr/share/icons/hicolor/128x128/apps/katu-logo.png
config/includes.chroot/usr/share/icons/hicolor/64x64/apps/katu-logo.png
config/includes.chroot/usr/share/icons/hicolor/48x48/apps/katu-logo.png
```

> **Para trocar:** substitua o arquivo PNG no tamanho correspondente.  
> Se quiser adicionar um novo app, crie o ícone em `256x256/apps/` e registre no `.desktop` com `Icon=katu-<nome>`.

---

## 9. Tema de ícones Katu — places e devices

**Onde aparecem:** gerenciador de arquivos (Dolphin), barra lateral, ícones de dispositivos no desktop.

### Ícones em 64×64

```
config/includes.chroot/usr/share/icons/katu/64x64/devices/katu-computer.png
config/includes.chroot/usr/share/icons/katu/64x64/devices/katu-network.png
config/includes.chroot/usr/share/icons/katu/64x64/devices/katu-removable-drive.png
config/includes.chroot/usr/share/icons/katu/64x64/devices/katu-usb.png
config/includes.chroot/usr/share/icons/katu/64x64/places/katu-home.png
config/includes.chroot/usr/share/icons/katu/64x64/places/katu-trash-empty.png
config/includes.chroot/usr/share/icons/katu/64x64/places/katu-trash-full.png
```

### Ícones em 32×32 (mesmos nomes)

```
config/includes.chroot/usr/share/icons/katu/32x32/devices/katu-computer.png
config/includes.chroot/usr/share/icons/katu/32x32/devices/katu-network.png
config/includes.chroot/usr/share/icons/katu/32x32/devices/katu-removable-drive.png
config/includes.chroot/usr/share/icons/katu/32x32/devices/katu-usb.png
config/includes.chroot/usr/share/icons/katu/32x32/places/katu-home.png
config/includes.chroot/usr/share/icons/katu/32x32/places/katu-trash-empty.png
config/includes.chroot/usr/share/icons/katu/32x32/places/katu-trash-full.png
```

### Arquivo de controle

```
config/includes.chroot/usr/share/icons/katu/index.theme
```

> O tema `katu` herda de `breeze-dark,breeze,hicolor` — ícones não customizados caem para o Breeze.

---

## 10. Logo global do sistema — pixmaps

**Onde aparece:** splash KDE, "Sobre este sistema" (KInfoCenter/About Distro), qualquer app que referencie `katu-logo`.

### Arquivo

```
config/includes.chroot/usr/share/pixmaps/katu-logo.png
```

> Este é o arquivo **mais referenciado** do sistema. Substitua-o para impactar simultaneamente:
> - Splash KDE Plasma (`Splash.qml → source: "/usr/share/pixmaps/katu-logo.png"`)
> - Tela "Sobre o sistema" (`kcm-about-distro.conf → LogoPath=/usr/share/pixmaps/katu-logo.png`)

---

## 11. Logos da marca — branding oficial no sistema

**Onde aparecem:** apps Katu que chamam os logos diretamente por caminho.

### Arquivos

```
config/includes.chroot/usr/share/katu/branding/logos/katu-os-dark.png
config/includes.chroot/usr/share/katu/branding/logos/katu-os-monochrome.png
config/includes.chroot/usr/share/katu/branding/logos/katu-os-white.png
config/includes.chroot/usr/share/katu/branding/logos/katu-symbol-monochrome.png
config/includes.chroot/usr/share/katu/branding/logos/katu-symbol-white.png
```

> Estes arquivos são a fonte canônica da marca dentro do sistema instalado.  
> São espelhados de `branding/logos/` no repositório.

---

## 12. Sobre o sistema — KDE About Distro

**Onde aparece:** `Configurações do Sistema → Sobre este computador`.

### Arquivo de controle

```
config/includes.chroot/etc/xdg/kcm-about-distro.conf
```

Conteúdo relevante:
```ini
LogoPath=/usr/share/pixmaps/katu-logo.png
```

> Para trocar o logo nessa tela: substitua `/usr/share/pixmaps/katu-logo.png`  
> (mesmo arquivo da seção 10) ou aponte `LogoPath` para outro caminho.

---

## 13. Desktop Live — Atalho do instalador (área de trabalho)

**Onde aparece:** ícone na área de trabalho do ambiente live (antes de instalar).

### Arquivo `.desktop`

```
config/includes.chroot/etc/skel/Área de Trabalho/katu-install.desktop  ← aparece no desktop do usuário live
config/includes.chroot/usr/share/applications/katu-install.desktop     ← versão no menu de apps
```

### Ícone referenciado

| `.desktop` | Campo `Icon=` | Arquivo resolvido |
|------------|---------------|-------------------|
| `katu-install.desktop` (skel) | `katu-logo` | `icons/hicolor/*/apps/katu-logo.png` |
| `katu-install.desktop` (applications) | `katu-installer` | `icons/hicolor/256x256/apps/katu-installer.png` |

---

## 14. Repositório de fontes / branding externo

Estes diretórios contêm os **arquivos originais / fontes de edição** — não são instalados no sistema, mas são de onde as imagens em `config/` devem ser geradas.

### `branding/logos/` — logos oficiais

```
branding/logos/katu-os-dark.png
branding/logos/katu-os-monochrome.png
branding/logos/katu-os-white.png
branding/logos/katu-symbol-monochrome.png
branding/logos/katu-symbol-white.png
```

### `branding/source/` — fontes de campanha

```
branding/source/banners-logo/banner-1.png  banner-2.png  banner-3.png
branding/source/logos-quadrados/logo-1.png … logo-20.png
branding/source/outros/outros-1.png … outros-5.png
branding/source/wallpapers-16x9/wallpaper-1.png … wallpaper-11.png
```

### `imagens/katu-os-final-assets/` — pack final estruturado

```
imagens/katu-os-final-assets/
  applications/      katu-backup, katu-feedback, katu-security, katu-system-info
  branding/logo/     katu-os-dark, monochrome, white, symbol-*
  grub/              katu-grub-logo, katu-selection
  installer/calamares/slides/  slide-01 … slide-06
  installer/live/    katu-live-welcome.png
  plasma/cursors/    katu-cursor-master.png
  plasma/icons/      katu-computer, katu-home, katu-network, katu-removable-drive, katu-trash-*, katu-usb
  plymouth/katu/     katu-logo-boot-light, progress-dot, spinner
  wallpapers/        katu-amazonia-4k, katu-dark-4k, katu-green-4k, katu-minimal-4k, katu-onca-4k, katu-rio-4k
```

> **Fluxo recomendado:** edite os originais em `imagens/katu-os-final-assets/` e  
> copie para os caminhos correspondentes em `config/includes.chroot/`.

---

## Mapa de propagação — onde cada arquivo "vai parar"

| Arquivo fonte (`imagens/katu-os-final-assets/`) | Destino no sistema instalado |
|-------------------------------------------------|------------------------------|
| `branding/logo/katu-os-dark.png` | `/usr/share/katu/branding/logos/katu-os-dark.png` |
| `grub/katu-grub-logo.png` | `/boot/grub/themes/katu/katu-grub-logo.png` |
| `installer/calamares/slides/slide-*.png` | `/etc/calamares/branding/katu/slide-*.png` |
| `installer/live/katu-live-welcome.png` | `/etc/calamares/branding/katu/welcome.png` |
| `plasma/icons/katu-*.png` | `/usr/share/icons/katu/64x64/{devices,places}/` |
| `plymouth/katu/logo.png` | `/usr/share/plymouth/themes/katu/logo.png` |
| `plymouth/katu/spinner.png` | `/usr/share/plymouth/themes/katu/spinner.png` |
| `plymouth/katu/progress-dot.png` | `/usr/share/plymouth/themes/katu/progress-dot.png` |
| `wallpapers/katu-*-4k.png` | `/usr/share/wallpapers/katu/contents/images/` |

---

## Checklist rápido — ao trocar a identidade visual

- [ ] `branding/logos/` — atualizar logos fonte
- [ ] `config/includes.binary/boot/grub/themes/katu/` — background + logo + selection
- [ ] `config/includes.chroot/boot/grub/themes/katu/` — mesmos 3 arquivos (cópia chroot)
- [ ] `config/includes.chroot/usr/share/plymouth/themes/katu/` — logo, spinner, progress-dot
- [ ] `config/includes.chroot/usr/share/sddm/themes/katu/` — background + logo
- [ ] `config/includes.chroot/usr/share/pixmaps/katu-logo.png` — logo global (impacta splash + about)
- [ ] `config/includes.chroot/usr/share/plasma/look-and-feel/org.katuos.desktop/contents/splash/Splash.qml` — verificar `source:` se muda o path
- [ ] `config/includes.chroot/usr/share/wallpapers/katu/contents/images/` — todos os wallpapers
- [ ] `config/includes.chroot/etc/calamares/branding/katu/` — logo, icon, welcome, slides
- [ ] `config/includes.chroot/usr/share/icons/hicolor/256x256/apps/` — todos os ícones de app
- [ ] `config/includes.chroot/usr/share/icons/katu/` — ícones places/devices (32 e 64)
- [ ] `config/includes.chroot/usr/share/katu/branding/logos/` — logos do sistema
- [ ] `installer/calamares/branding/katu/` — sincronizar com o diretório acima

---

*Documento gerado por auditoria automática do repositório `C:\katuos`.*
