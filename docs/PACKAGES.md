# Katu OS — Pacotes Customizados

Quatro pacotes `.deb` próprios compõem a identidade do Katu OS.

## katu-release

**Versão:** 1.0 | **Arch:** all | **Prioridade:** required

Identidade da distribuição.

| Arquivo instalado | Conteúdo |
|-------------------|----------|
| `/etc/os-release` | `NAME="Katu OS"`, `ID=katu`, `ID_LIKE=debian` |
| `/etc/katu-release` | `KATU_VERSION=1.0`, `KATU_BUILD=alpha`, `KATU_BASE=Debian 13 Trixie` |
| `/usr/share/katu/` | Recursos da distribuição |

Usado por: `hostnamectl`, `lsb_release`, KDE about-distro, neofetch/fastfetch.

---

## katu-branding

**Versão:** 1.0 | **Arch:** all | **Deps:** katu-release

Recursos visuais da distribuição.

| Conteúdo | Localização |
|----------|-------------|
| 6 wallpapers 4K | `/usr/share/wallpapers/katu/` |
| Logo em variantes | `/usr/share/katu/branding/logos/` |
| Ícones do sistema | `/usr/share/icons/katu/` |
| Ícones hicolor | `/usr/share/icons/hicolor/{256,128,64,48}x*/apps/` |
| Tema de cores KDE | `/usr/share/color-schemes/KatuDark.colors` |
| Tema de cores KDE | `/usr/share/color-schemes/KatuLight.colors` |

---

## katu-default-settings

**Versão:** 1.0 | **Arch:** all | **Deps:** katu-branding

Configurações padrão do KDE Plasma para novos usuários (via `/etc/skel`).

| Arquivo skel | Configura |
|--------------|-----------|
| `.config/kdeglobals` | ColorScheme, fonte Noto Sans, locale PT-BR |
| `.config/kwinrc` | Compositor OpenGL, atalhos de janela |
| `.config/mimeapps.list` | Firefox como browser padrão, VLC para vídeo |
| `.config/powerdevilrc` | Gerenciamento de energia |
| `.config/konsolerc` | Perfil Katu como padrão |
| `.config/plasmarc` | Tema de widgets |
| `.config/kscreenlockerrc` | Wallpaper na tela de bloqueio |
| `.local/share/konsole/katu.profile` | Perfil Konsole Amazônia Dark |
| `.local/share/konsole/KatuDark.colorscheme` | Cores Konsole |

---

## katu-welcome

**Versão:** 1.0 | **Arch:** all | **Deps:** python3, python3-pyqt5, katu-release

Aplicativo de boas-vindas executado no primeiro login.

| Arquivo | Função |
|---------|--------|
| `/usr/bin/katu-welcome` | Executável (wrapper) |
| `/usr/lib/katu-welcome/main.py` | Aplicativo PyQt5 principal |
| `/usr/share/applications/katu-welcome.desktop` | Entrada no menu |
| `/etc/xdg/autostart/katu-welcome-firstboot.desktop` | Autostart condicional |

**Mecanismo de primeiro boot:**
- Instalação cria `/etc/katu-firstboot`
- katu-welcome remove esse arquivo na primeira execução
- Usuário pode ativar/desativar autostart via checkbox na UI

## Compilar os pacotes

```bash
# Em ambiente Linux (WSL2 ou VM)
for pkg in katu-release katu-branding katu-default-settings katu-welcome; do
    dpkg-deb --build --root-owner-group packages/$pkg output/${pkg}_1.0_all.deb
done
```

Ou via script completo: `bash scripts/build.sh`
