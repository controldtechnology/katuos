# TROUBLESHOOTING — KATU OS

---

## Problemas de build

### lb build falha com "permission denied"

```bash
sudo bash scripts/build.sh
```
O live-build requer root.

### "debootstrap: command not found"

```bash
sudo apt-get install debootstrap
```

### "No space left on device"

O build precisa de ~20 GB livres. Libere espaço ou use outro disco:
```bash
export TMPDIR=/mnt/disco-grande
sudo bash scripts/build.sh
```

### "Cannot connect to Debian mirrors"

Verifique conexão com a internet. Teste:
```bash
curl https://deb.debian.org/debian/dists/trixie/Release
```

Se estiver atrás de proxy:
```bash
export http_proxy=http://proxy:porta
export https_proxy=http://proxy:porta
sudo -E bash scripts/build.sh
```

### Erro de assinatura de pacote

```
WARNING: The following packages cannot be authenticated!
```

Instalar chaves Debian:
```bash
sudo apt-get install -y debian-keyring
```

---

## Problemas de boot

### ISO não inicia no pendrive

- Verificar se a gravação foi feita corretamente (use balenaEtcher ou Rufus)
- Tentar outro pendrive
- Verificar configurações de boot no BIOS (UEFI vs Legacy)

### Tela preta após boot

Adicionar `nomodeset` nas opções de boot do GRUB:
1. No menu GRUB, pressionar `e`
2. Na linha `linux`, adicionar `nomodeset` antes de `quiet splash`
3. Pressionar Ctrl+X para iniciar

### GRUB não aparece

- Verificar se o computador está em UEFI mode
- Desabilitar Secure Boot temporariamente
- Tentar Legacy BIOS mode

---

## Problemas de hardware

### Wi-Fi não funciona

```bash
# Ver qual firmware está faltando
dmesg | grep -i firmware

# Instalar firmware adicional
sudo apt-get install firmware-nonfree
```

### Áudio sem som

```bash
# Verificar dispositivos
aplay -l

# Reinstalar PipeWire
sudo apt-get install --reinstall pipewire pipewire-pulse
```

### NVIDIA — tela preta

```bash
# Usar modo de segurança (nomodeset no GRUB)
# Depois instalar driver NVIDIA via katu-welcome
```

---

## Problemas de instalação (Calamares)

### "Failed to create partition"

- Verificar se o disco não está montado
- Usar `gparted` para desfazer partições problemáticas antes
- Reiniciar e tentar novamente

### Instalação trava em X%

- Verificar logs: `/var/log/calamares/session.log`
- Geralmente relacionado a escrita de disco lenta

---

## Logs úteis

```bash
# Live system
journalctl -b 0

# Calamares
cat /var/log/calamares/session.log

# Build
tail -200 logs/build-*.log
```
