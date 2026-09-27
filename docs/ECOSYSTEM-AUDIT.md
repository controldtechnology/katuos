# ECOSYSTEM AUDIT — KATU OS

Data: 2026-09-27

---

## Distribuição Base

| Item          | Valor |
|---------------|-------|
| Base          | Debian 13 Trixie |
| KDE Plasma    | 6.x (trixie) |
| Qt            | 6.x |
| Kernel        | Linux 6.x (trixie) |
| Python        | 3.11+ |
| live-build    | Debian Trixie |
| Arquitetura   | amd64 |

## Estrutura do Projeto

```
C:\katuos\
├── config/           # live-build configuration
│   ├── archives/     # APT sources for build
│   ├── bootloaders/  # GRUB config
│   ├── hooks/live/   # Chroot hooks (0001-0096, 9999)
│   ├── includes.binary/ # Binary-stage includes
│   ├── includes.chroot/ # Chroot includes (sddm, plymouth, plasma, etc.)
│   └── package-lists/   # APT package lists
├── packages/         # Katu custom Debian packages
│   ├── katu-branding/
│   ├── katu-default-settings/
│   ├── katu-ia/
│   ├── katu-installer/
│   ├── katu-release/
│   ├── katu-welcome/
│   └── katu-xampp/
├── installer/        # Calamares config
├── plasma/           # KDE Plasma theme
├── sddm/             # SDDM theme
├── plymouth/         # Plymouth theme
├── grub/             # GRUB theme
├── branding/         # Logos, tokens, wallpapers
├── scripts/          # Build + test scripts
├── docs/             # Documentation
└── dist/             # Built ISOs
```

## Hooks Existentes

| Hook | Função |
|------|--------|
| 0001 | Locale pt_BR |
| 0002 | Timezone Sao_Paulo |
| 0003 | Teclado ABNT2 |
| 0004 | Initramfs Live |
| 0005 | Google Chrome |
| 0006 | LAMP stack |
| 0007 | Python libs para IA |
| 0010 | SDDM Katu |
| 0011 | Plasma tema Amazônia Dark |
| 0020 | Plymouth Katu |
| 0030 | Diretórios em português |
| 0040 | Flatpak (sem Flathub auto) |
| 0050 | Sudo |
| 0060 | Serviços systemd |
| 0065 | UFW firewall |
| 0070 | Firefox ESR |
| 0071 | Firefox pt-BR |
| 0080 | Konsole Amazônia Dark |
| 0085 | Apps padrão |
| 0090 | Fastfetch |
| 0091 | Usuário live |
| 0092 | KDE settings |
| 0093 | Splash screen KDE |
| 0095 | Serviços Katu |
| 0096 | QA live smoke |
| 9999 | Limpeza final |

## Pacotes Instalados (package-lists/)

**katu.list.chroot:** katu-branding, katu-default-settings, katu-welcome,
katu-release, calamares, katu-installer, katu-ia, katu-xampp, flatpak,
kdeconnect, ufw, gufw, bluetooth, bluez, blueman, plasma-systemmonitor

**apps.list.chroot:** firefox-esr, libreoffice (suite completa pt-BR),
vlc, okular, gwenview, kate, ark, cups, htop, curl, wget

**kde.list.chroot:** plasma-desktop, plasma-workspace, plasma-nm, kwin,
dolphin, konsole, kate, breeze, sddm

**firmware.list.chroot:** firmware-linux-free, firmware-linux-nonfree

**localization.list.chroot:** locales-all, language-pack-pt, etc.

## Aplicativos Katu Existentes (implementação parcial)

### katu-ia (desenvolvedores)
- **Localização:** packages/katu-ia/usr/lib/katu-ia/katu_ia.py
- **Status:** Funcional (PyQt5)
- **Providers:** Claude, OpenAI, Gemini, Ollama
- **Config:** ~/.config/katu/ai/config.json
- **Desktop:** katu-ia.desktop
- **Observação:** Focado em desenvolvedores. katu-ai será a versão para usuários finais.

### katu-welcome
- **Localização:** packages/katu-welcome/usr/lib/katu-welcome/main.py
- **Status:** Funcional básico (PyQt5)
- **Observação:** Será evoluído para onboarding completo (9 etapas)

### katu-installer
- **Localização:** packages/katu-installer/usr/lib/katu-installer/instalador.py
- **Status:** Funcional (atalho para Calamares)

### katu-xampp
- **Localização:** packages/katu-xampp/usr/lib/katu-xampp/katu_xampp.py
- **Status:** Funcional (gerenciador LAMP)

## Serviços Existentes

- NetworkManager
- SDDM
- bluetooth/bluez
- ufw
- cups
- systemd (init)

## DBus / Polkit

- KDE Connect usa DBus
- Plasma Notifications via DBus
- PackageKit disponível (plasma-discover-backend-flatpak instalado)

## Infraestrutura Ausente (a criar)

### Python
- katu_core: biblioteca central (não existe)
- katu_ui: UI kit compartilhado (não existe)

### Apps (a criar como novos pacotes)
- katu-central: painel principal
- katu-ai: assistente IA para usuários
- katu-store: loja de apps
- katu-update: gerenciador de atualizações
- katu-drivers: gerenciador de drivers
- katu-connect: interface KDE Connect
- katu-backup: backup/restauração
- katu-webapps: gerenciador web apps
- katu-help: central de ajuda
- katu-diagnostic: diagnóstico do sistema
- katu-feedback: feedback

### Serviços (a criar)
- katu-update-service: verificação periódica de atualizações (systemd timer)

## Ícones Disponíveis (katu-branding)

```
usr/share/icons/hicolor/
├── 48x48/apps/katu-logo.png
├── 64x64/apps/katu-logo.png
├── 128x128/apps/katu-logo.png
└── 256x256/apps/
    ├── katu-logo.png
    ├── katu-backup.png
    ├── katu-feedback.png
    ├── katu-security.png
    └── katu-system-info.png
```

## Identidade Visual

Paleta (katu-tokens.json):
- BG:          #0d1117
- SURFACE:     #161b22
- CARD:        #1c2128
- BORDER:      #30363d
- ACCENT:      #00c853
- ACCENT_H:    #00e676
- ACCENT_A:    #00a040
- AMBER:       #ffab00
- TEXT:        #e6edf3
- MUTED:       #8b949e
- ERROR:       #f85149
- INFO:        #58a6ff

Fontes: Noto Sans (interface), Noto Mono (código)

## Conclusão da Auditoria

O projeto possui base sólida com:
- Build pipeline funcional (CI/CD GitHub Actions)
- ISO funcional testada
- 2 apps Python funcionais (katu-ia, katu-welcome)
- Identidade visual definida
- Estrutura de packaging Debian

Gaps para o Ecossistema:
- Sem katu-core (biblioteca centralizada)
- Sem painel de controle (katu-central)
- Sem loja de apps (katu-store)
- Sem gerenciador de atualizações (katu-update)
- Sem gerenciador de drivers (katu-drivers)
- katu-ai (usuário final) ainda não existe
- katu-backup, katu-webapps, katu-help, katu-diagnostic, katu-feedback: não existem

Estratégia: evoluir katu-welcome e katu-ia, criar os demais do zero
seguindo o mesmo padrão Python/PyQt5 já estabelecido.
