# CRIAR PENDRIVE — KATU OS

Como gravar a ISO do Katu OS em um pendrive para instalar ou testar.

**AVISO**: Gravar o pendrive APAGA todo o conteúdo existente.

Certifique-se de selecionar o pendrive correto.

---

## Windows

### Opção 1: balenaEtcher (recomendado)

1. Baixar em: https://etcher.balena.io
2. Abrir o balenaEtcher
3. Clicar em "Flash from file" → selecionar `katu-os-1.0-amd64.iso`
4. Clicar em "Select target" → selecionar o pendrive
5. Clicar em "Flash!"
6. Aguardar conclusão

### Opção 2: Rufus

1. Baixar em: https://rufus.ie
2. Abrir o Rufus como Administrador
3. Selecionar o pendrive em "Device"
4. Em "Boot selection", escolher a ISO do Katu OS
5. Em "Partition scheme", selecionar:
   - **GPT** para computadores com UEFI (recomendado)
   - **MBR** para computadores antigos com Legacy BIOS
6. Clicar em "START"
7. Se perguntar sobre modo ISO: selecionar **"Write in ISO Image mode"**

---

## Linux

### Opção 1: Interface gráfica (KDE Partition Manager / GNOME Disks)

No KDE: Abrir KDE Partition Manager → selecionar pendrive → Restaurar → selecionar ISO

### Opção 2: Terminal (dd)

```bash
# IMPORTANTE: Substituir /dev/sdX pelo pendrive correto
# Verificar o dispositivo com: lsblk

sudo dd if=katu-os-1.0-amd64.iso \
        of=/dev/sdX \
        bs=4M \
        status=progress \
        conv=fsync

sudo sync
```

**NUNCA execute `dd` sem ter certeza absoluta do dispositivo correto.**

---

## Iniciar pelo pendrive

1. Inserir o pendrive
2. Reiniciar o computador
3. Durante o POST, pressionar a tecla de boot menu:
   - Dell: F12
   - HP: F9
   - Lenovo: F12
   - ASUS: F8 ou ESC
   - MSI: F11
4. Selecionar o pendrive
5. Aguardar o menu do Katu OS aparecer

---

## Verificar integridade antes de gravar

```bash
# Linux/WSL
sha256sum -c katu-os-1.0-amd64.iso.sha256

# Windows PowerShell
certutil -hashfile katu-os-1.0-amd64.iso SHA256
# Comparar com o conteúdo de katu-os-1.0-amd64.iso.sha256
```
