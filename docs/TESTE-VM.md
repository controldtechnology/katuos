# TESTE EM MÁQUINA VIRTUAL — KATU OS

Como testar o Katu OS em máquinas virtuais.

---

## VirtualBox

### Configuração recomendada

| Configuração | Valor |
|-------------|-------|
| Sistema | Linux → Debian (64-bit) |
| RAM | 4096 MB (mínimo 2048) |
| Disco | 40 GB (VDI, dinamicamente alocado) |
| Vídeo | 128 MB, aceleração 3D habilitada |
| Rede | Adaptador em modo Bridge ou NAT |
| USB | USB 3.0 habilitado |

### Passos

1. Criar nova VM
2. Em "Sistema → Processador", habilitar "Habilitar PAE/NX"
3. Em "Armazenamento", adicionar a ISO como disco óptico
4. Em "Sistema → Placa Mãe", habilitar EFI (se testar UEFI)
5. Iniciar a VM
6. No menu GRUB, selecionar "Experimentar Katu OS"

### EFI no VirtualBox

Habilitar: Configurações → Sistema → Placa Mãe → Habilitar EFI

---

## QEMU/KVM

### Testar com BIOS (Legacy)

```bash
qemu-system-x86_64 \
    -m 4096 \
    -cdrom output/katu-os-1.0-amd64.iso \
    -boot d \
    -vga virtio \
    -netdev user,id=n0 \
    -device virtio-net,netdev=n0 \
    -enable-kvm \
    -smp 2
```

### Testar com UEFI

```bash
qemu-system-x86_64 \
    -m 4096 \
    -bios /usr/share/ovmf/OVMF.fd \
    -cdrom output/katu-os-1.0-amd64.iso \
    -boot d \
    -vga virtio \
    -netdev user,id=n0 \
    -device virtio-net,netdev=n0 \
    -enable-kvm \
    -smp 2
```

### Testar instalação completa

```bash
# Criar disco virtual de 40GB
qemu-img create -f qcow2 katu-test.qcow2 40G

# Boot pela ISO
qemu-system-x86_64 \
    -m 4096 \
    -bios /usr/share/ovmf/OVMF.fd \
    -cdrom output/katu-os-1.0-amd64.iso \
    -drive file=katu-test.qcow2,format=qcow2 \
    -boot d \
    -vga virtio \
    -netdev user,id=n0 \
    -device virtio-net,netdev=n0 \
    -enable-kvm \
    -smp 2

# Após instalar, boot pelo disco instalado:
qemu-system-x86_64 \
    -m 4096 \
    -bios /usr/share/ovmf/OVMF.fd \
    -drive file=katu-test.qcow2,format=qcow2 \
    -vga virtio \
    -netdev user,id=n0 \
    -device virtio-net,netdev=n0 \
    -enable-kvm \
    -smp 2
```

---

## VMware (Workstation/Player)

1. Criar nova VM → Típica
2. Selecionar ISO do Katu OS
3. Escolher "Linux → Debian 11 ou 12 64-bit"
4. RAM: 4096 MB
5. Disco: 40 GB
6. Iniciar

---

## Itens a verificar na VM

```
[ ] Menu GRUB aparece com tema Katu
[ ] Plymouth exibe logo durante boot
[ ] SDDM aparece com tema Katu
[ ] Login com usuário live funciona
[ ] KDE Plasma carrega
[ ] Wallpaper Katu aparece
[ ] Internet funciona (NAT)
[ ] Calamares abre via ícone no desktop
[ ] Instalação via Calamares conclui
[ ] Sistema instalado inicia
[ ] Katu Welcome abre
[ ] APT funciona (apt-get update)
[ ] Desligar funciona
```
