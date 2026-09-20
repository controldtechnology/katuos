# ARQUITETURA — KATU OS

Versão: 1.0  
Última atualização: 2026-09-20

---

## 1. VISÃO GERAL

```
┌─────────────────────────────────────────────────────────┐
│                       KATU OS 1.0                       │
│                                                         │
│   "Livre. Brasileiro. Para todos."                      │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                     BASE: DEBIAN 13                     │
│                       "Trixie"                          │
│              debian-live-13.7.0-amd64                   │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                   LIVE-BUILD SYSTEM                     │
│                                                         │
│  config/                                                │
│  ├── package-lists/   ← pacotes instalados              │
│  ├── includes.chroot/ ← arquivos no sistema             │
│  ├── includes.binary/ ← arquivos na ISO                 │
│  ├── hooks/           ← scripts pós-instalação          │
│  ├── bootloaders/     ← GRUB config                     │
│  └── archives/        ← repositórios extras             │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                   PACOTES PRÓPRIOS                      │
│                                                         │
│  katu-branding         ← logos, wallpapers, assets      │
│  katu-default-settings ← configurações Plasma           │
│  katu-welcome          ← app boas-vindas                │
│  katu-release          ← /etc/os-release, versão        │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                  COMPONENTES VISUAIS                    │
│                                                         │
│  KDE Plasma          ← desktop principal                │
│  SDDM                ← tela de login                    │
│  Plymouth            ← splash de boot                   │
│  GRUB                ← bootloader                       │
│  Calamares           ← instalador                       │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                   OUTPUT FINAL                          │
│                                                         │
│  output/katu-os-1.0-amd64.iso                           │
│  output/katu-os-1.0-amd64.iso.sha256                    │
│  output/build-info.txt                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. CAMADAS DO SISTEMA

### Camada 1: Base Debian

```
Debian 13 Stable (Trixie)
├── Kernel Linux 6.1+ (amd64)
├── systemd
├── APT + dpkg
├── Repositórios oficiais Debian
│   ├── main
│   ├── contrib
│   └── non-free (firmware)
└── debootstrap bootstrap
```

### Camada 2: Desktop KDE Plasma

```
KDE Plasma 6.x
├── plasma-desktop
├── plasma-workspace
├── kwin (compositor)
├── dolphin (gerenciador de arquivos)
├── konsole (terminal)
├── spectacle (capturas de tela)
├── kde-spectacle
└── discover (loja de apps)
```

### Camada 3: Experiência Katu

```
Katu Experience
├── katu-branding
│   ├── wallpapers
│   ├── logos
│   └── assets
├── katu-default-settings
│   ├── Plasma theme
│   ├── SDDM theme
│   ├── Plymouth theme
│   └── GRUB theme
├── katu-welcome
│   └── app de boas-vindas
└── katu-release
    └── /etc/os-release
```

### Camada 4: Instalador

```
Calamares
├── branding katu
├── módulos configurados
├── fluxo simplificado
└── suporte UEFI + Legacy
```

---

## 3. FERRAMENTA DE BUILD

### live-build

Ferramenta oficial Debian para criar distribuições derivadas.

```bash
lb config    # configura o build
lb build     # executa o build
lb clean     # limpa artefatos
```

Documentação: https://live-team.pages.debian.net/live-manual/

### Requisitos de build

```
Sistema: Debian/Ubuntu Linux
Privilégios: root ou sudo
Ferramentas: live-build, debootstrap, xorriso, squashfs-tools
Espaço: ~20 GB durante build
Tempo estimado: 30-90 minutos
```

---

## 4. CONFIGURAÇÃO LIVE-BUILD

Arquivo principal: `config/live-build.conf`

Parâmetros críticos:

```bash
LB_DISTRIBUTION="trixie"
LB_ARCHITECTURE="amd64"
LB_BOOTLOADERS="grub-efi,grub-pc"
LB_DEBIAN_INSTALLER="none"
LB_MEMTEST="none"
LB_WIN32_LOADER="false"
LB_ISO_APPLICATION="Katu OS"
LB_ISO_PREPARER="Katu OS Team"
LB_ISO_PUBLISHER="Katu OS"
```

---

## 5. REPOSITÓRIOS APT

```
deb https://deb.debian.org/debian trixie main contrib non-free non-free-firmware
deb https://deb.debian.org/debian trixie-updates main contrib non-free non-free-firmware
deb https://deb.debian.org/debian-security trixie-security main contrib non-free non-free-firmware
```

---

## 6. FILOSOFIA DE BUILD

```
"Debian faz a base. Katu cria a experiência."
```

Princípios:
- Não modificar pacotes Debian upstream desnecessariamente
- Adicionar configurações via includes, não patches
- Usar hooks para ajustes pós-instalação
- Pacotes próprios apenas para branding e configurações
- Manter compatibilidade total com APT/dpkg Debian

---

## 7. ESTRUTURA DE ARQUIVOS

```
C:\katuos\
├── base/                    # ISO Debian base
├── build/                   # Diretório de trabalho live-build
├── config/                  # Configuração live-build
├── packages/                # Pacotes .deb próprios
├── branding/                # Assets de identidade visual
├── wallpapers/              # Wallpapers
├── plasma/                  # Configuração KDE Plasma
├── sddm/                    # Tema SDDM
├── plymouth/                # Tema Plymouth
├── grub/                    # Tema GRUB
├── installer/               # Configuração Calamares
├── scripts/                 # Scripts de build
├── docs/                    # Documentação
├── logs/                    # Logs de build
└── output/                  # ISO gerada
```

---

## 8. FLUXO DE BUILD

```
scripts/setup-build-env.sh
        │
        ▼
   Instala dependências
   Verifica ambiente
        │
        ▼
scripts/build.sh
        │
        ├── 1. Constrói pacotes Debian
        │   └── packages/*.deb
        │
        ├── 2. Configura live-build
        │   └── lb config [parâmetros]
        │
        ├── 3. Executa build
        │   └── lb build
        │
        ├── 4. Gera checksum
        │   └── sha256sum
        │
        └── 5. Output
            └── output/katu-os-1.0-alpha-amd64.iso
```

---

## 9. IDENTIDADE DO SISTEMA

```
/etc/os-release:
NAME="Katu OS"
PRETTY_NAME="Katu OS 1.0"
VERSION="1.0"
VERSION_ID="1.0"
ID=katu
ID_LIKE=debian
VERSION_CODENAME=stable

/etc/katu-release:
KATU_VERSION=1.0
KATU_ARCH=amd64
KATU_BUILD=alpha
KATU_BASE=Debian 13 Trixie
```

---

## 10. CHECKPOINTS DE BUILD

| Build | Objetivo | Critério de sucesso |
|-------|----------|---------------------|
| BUILD-001 | ISO mínima Debian Live | Boot confirma sistema |
| BUILD-002 | KDE Plasma funcionando | Desktop aparece, Wi-Fi funciona |
| BUILD-003 | Branding Katu | Visual Katu presente |
| BUILD-004 | Calamares integrado | Instalação completa funciona |
| BUILD-005 | Apps + drivers | Conjunto completo funcional |
| BUILD-006 | Katu Welcome | App abre no primeiro login |
| BUILD-007 | QA completo | Todos os testes críticos passam |
| RC-001 | Release Candidate | Distribuível para teste público |
| 1.0 | Release final | Release notes publicados |

---

*Documento vivo — atualizar a cada fase de desenvolvimento*
