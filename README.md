# KATU OS

> **Livre. Brasileiro. Para todos.**

Katu OS é uma distribuição Linux brasileira baseada em Debian Stable com KDE Plasma.  
Projetada para ser simples, leve, moderna e acessível para qualquer pessoa.

---

## Identidade

- **Base**: Debian 13 "Trixie" Stable
- **Desktop**: KDE Plasma
- **Arquitetura**: amd64 (ARM64 planejado)
- **Idioma padrão**: Português (Brasil)
- **Versão**: 1.0-alpha

---

## Objetivo

Uma pessoa sem experiência com Linux deve conseguir:

```
Baixar ISO → Gravar pendrive → Iniciar computador → Experimentar → Instalar → Usar
```

---

## Preparar ambiente de build

O build **requer Linux** (Debian/Ubuntu recomendado).

No Windows, habilite WSL2 primeiro:
```
1. BIOS/UEFI: habilitar Intel VT-x
2. wsl --install
3. wsl --install -d Debian
```

Depois, no terminal Debian/Ubuntu:

```bash
# Clonar ou copiar o projeto
git clone <repo> ~/katuos
cd ~/katuos

# Instalar dependências
bash scripts/setup-build-env.sh

# Executar build
bash scripts/build.sh
```

A ISO será gerada em:
```
output/katu-os-1.0-alpha-amd64.iso
```

---

## Estrutura do projeto

```
katuos/
├── base/           # ISO Debian base
├── config/         # Configuração live-build
├── packages/       # Pacotes .deb próprios
├── branding/       # Logos e identidade visual
├── wallpapers/     # Wallpapers
├── plasma/         # Tema KDE Plasma
├── sddm/           # Tema tela de login
├── plymouth/       # Splash de boot
├── grub/           # Tema bootloader
├── installer/      # Configuração Calamares
├── scripts/        # Scripts de build
├── docs/           # Documentação
└── output/         # ISO gerada
```

---

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura do projeto |
| [docs/BUILD.md](docs/BUILD.md) | Instruções de build |
| [docs/AUDITORIA-INICIAL.md](docs/AUDITORIA-INICIAL.md) | Auditoria inicial |
| [docs/STATUS.md](docs/STATUS.md) | Status atual |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Roadmap |
| [docs/TESTING.md](docs/TESTING.md) | Guia de testes |
| [docs/RELEASE.md](docs/RELEASE.md) | Processo de release |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Resolução de problemas |

---

## Filosofia

```
Debian faz a base.
Katu cria a experiência.
```

- Não modificar pacotes Debian upstream desnecessariamente
- Privacidade por padrão
- Sem telemetria oculta
- Compatibilidade total com repositórios Debian
- Hardware suportado = hardware testado

---

## Licença

Código Katu OS: MIT License  
Componentes Debian/KDE: licenças originais preservadas  
Marca "Katu OS": reservada

Ver [docs/LICENSES.md](docs/LICENSES.md) para detalhes completos.
