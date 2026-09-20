# BUILD — KATU OS

Guia completo para compilar o Katu OS a partir do código-fonte.

---

## Requisitos do sistema de build

| Requisito | Mínimo | Recomendado |
|-----------|--------|-------------|
| SO | Debian 12+ / Ubuntu 22.04+ | Debian 13 Trixie |
| RAM | 4 GB | 8 GB |
| Disco livre | 30 GB | 50 GB |
| CPU | qualquer x86_64 | multi-core |
| Internet | sim | sim |

**No Windows**: Habilite WSL2 primeiro (ver abaixo).

---

## Preparação no Windows (WSL2)

### 1. Habilitar virtualização no BIOS/UEFI

- Reiniciar e entrar no BIOS/UEFI (Del, F2, F10 ou F12)
- Habilitar "Intel Virtualization Technology" ou "AMD-V"
- Salvar e reiniciar

### 2. Instalar WSL2

```powershell
wsl --install
# Reiniciar
wsl --install -d Debian
```

### 3. Copiar projeto para WSL2

```bash
# No terminal WSL2 (Debian)
cp -r /mnt/c/katuos ~/katuos
cd ~/katuos
```

---

## Preparar ambiente de build

```bash
sudo bash scripts/setup-build-env.sh
```

Este script instala:
- `live-build` — ferramenta oficial Debian para ISOs
- `debootstrap` — bootstrap do sistema base
- `squashfs-tools` — compressão do filesystem
- `xorriso` — geração da ISO
- `grub-*` — bootloader GRUB
- Dependências adicionais

---

## Executar o build

```bash
sudo bash scripts/build.sh
```

O build executa as seguintes etapas:

1. **Construir pacotes** — compila katu-*.deb de `packages/`
2. **Configurar live-build** — `lb config` com parâmetros Katu
3. **Executar lb build** — cria o chroot, instala pacotes, comprime
4. **Mover ISO** — para `output/katu-os-1.0-alpha-amd64.iso`
5. **Checksum** — gera `output/katu-os-1.0-alpha-amd64.iso.sha256`

**Tempo estimado**: 30 a 90 minutos (depende da velocidade da internet e do hardware)

---

## Resultado esperado

```
output/
├── katu-os-1.0-alpha-amd64.iso       ← ISO bootável
├── katu-os-1.0-alpha-amd64.iso.sha256 ← Checksum
└── build-info.txt                     ← Metadados do build
```

---

## Limpar build

```bash
# Limpeza parcial (preserva cache)
bash scripts/clean.sh

# Limpeza completa
bash scripts/clean.sh full
```

---

## Validar projeto

```bash
bash scripts/validate.sh
```

---

## Sequência de builds

| Build | Comando | Objetivo |
|-------|---------|---------|
| BUILD-001 | `bash scripts/build.sh` | ISO mínima Debian Live |
| BUILD-002 | (após ajustes KDE) | KDE Plasma funcionando |
| BUILD-003 | (após branding) | Visual Katu |
| BUILD-004 | (após Calamares) | Instalação funciona |

---

## Troubleshooting

Ver [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Logs

Os logs de build ficam em:

```
logs/build-YYYYMMDD-HHMMSS.log
```

Em caso de falha, verifique as últimas linhas do log:

```bash
tail -100 logs/build-*.log | less
```
