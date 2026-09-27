# ECOSYSTEM BASELINE — KATU OS

Data: 2026-09-27
Branch: visual/katu-brand-identity
Commit: 601c73e

---

## ISO Funcional Atual

| Campo         | Valor |
|---------------|-------|
| **Arquivo**   | katu-os-1.0.1-rc1-amd64.iso |
| **Caminho**   | dist/smoke-diag-36261032057/katu-os-test-candidate-36261032057/candidate-20260926T180402Z-0bc565b0/ |
| **Tamanho**   | 3.25 GB (3.488.020.480 bytes) |
| **SHA-256**   | 327b2d376abd738e1f49643ba8b7cd59e8b4cfe15d4e76af63adf95df5df7142 |
| **Data**      | 2026-09-26 15:52 |
| **Versão**    | 1.0.1-rc1 |
| **Pipeline**  | GitHub Actions build-iso.yml / scripts/build-clean.sh |
| **Branch**    | visual/katu-brand-identity |

## Status Funcional da ISO Atual

| Componente     | Status         | Observações |
|----------------|----------------|-------------|
| GRUB           | OK             | UEFI + BIOS/Legacy |
| Plymouth       | OK             | Tema Katu com logo |
| Live           | OK             | Autologin como usuário katu |
| Plasma         | OK             | KDE Plasma com tema Amazônia Dark |
| SDDM           | OK             | Tema Katu, Qt 6 |
| Calamares      | OK             | Instalador configurado |
| Instalação     | OK (manual)    | Validado em VirtualBox BIOS/Legacy |
| Reboot         | OK             | Sistema instalado inicia |
| Login          | OK             | SDDM → Plasma |
| Rede           | OK             | NetworkManager ativo |
| Áudio          | NÃO TESTADO    | PipeWire incluído |
| Bluetooth      | NÃO TESTADO    | bluez/blueman incluídos |

## Pacotes Katu Existentes (na ISO atual)

| Pacote                  | Versão | Descrição |
|-------------------------|--------|-----------|
| katu-branding           | 1.0    | Logos, wallpapers, ícones Katu |
| katu-default-settings   | 1.0    | Configurações padrão KDE |
| katu-welcome            | 1.0    | App de boas-vindas (básico) |
| katu-release            | 1.0    | /etc/os-release e /etc/katu-release |
| katu-ia                 | 1.0    | Hub IA para desenvolvedores |
| katu-installer          | 1.0    | Atalho para Calamares |
| katu-xampp              | 1.0    | Gerenciador LAMP/XAMPP |

## Pipeline de Build

1. `scripts/build-clean.sh` (como root)
2. Preflight checks + testes Python
3. `dpkg-deb` constrói todos os `packages/*` → `.deb`
4. Repositório APT local via `dpkg-scanpackages`
5. `lb config` → `lb bootstrap` → `lb chroot` → `lb binary`
6. Validações: `validate-iso.sh`, `test-iso.sh`, `release-gate.py`
7. ISO gerada em `output/candidate-STAMP-COMMIT/`

## Dependências Principais

- live-build (Debian Trixie)
- debootstrap
- squashfs-tools
- xorriso
- dpkg-dev
- python3-pyqt5
- Debian 13 Trixie como base

## Regras de Preservação

A ISO original NÃO deve ser sobrescrita. A nova ISO do Ecossistema
deve receber outro nome:

`katu-os-1.0.1-ecosystem-amd64.iso`

NÃO alterar sem necessidade:
- kernel e initramfs
- firmware e drivers existentes
- GRUB funcional (UEFI + BIOS)
- squashfs e configuração Live
- Calamares funcional
- hooks de rede, áudio, Bluetooth
- Configuração de hardware
