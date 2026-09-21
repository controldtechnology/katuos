# Katu OS — Guia de Testes

Para a matriz de testes completa (casos de teste individuais), consulte `docs/MATRIZ-TESTES.md`.

## Ambiente de Teste Recomendado

### VirtualBox (Windows/Linux/macOS)
```
RAM: 4096 MB
CPU: 2 cores, Enable VT-x/AMD-V
Disco: 30 GB VDI (dinâmico)
Rede: NAT
Gráficos: 128 MB, aceleração 3D habilitada
Boot: UEFI (habilitar via EFI checkbox)
```

### QEMU/KVM (Linux)
```bash
# UEFI
qemu-system-x86_64 \
  -m 4G -smp 2 \
  -bios /usr/share/ovmf/OVMF.fd \
  -cdrom katu-os-1.0-amd64.iso \
  -boot d \
  -vga virtio \
  -display gtk

# BIOS Legacy
qemu-system-x86_64 \
  -m 4G -smp 2 \
  -cdrom katu-os-1.0-amd64.iso \
  -boot d
```

## Fases de Teste

### Fase 1 — Boot

- [ ] GRUB carrega com tema Katu
- [ ] Plymouth aparece com logo e spinner
- [ ] SDDM carrega com tema Katu
- [ ] Login automático do usuário live funciona

### Fase 2 — Live System

- [ ] KDE Plasma carrega com wallpaper Amazônia
- [ ] Locale pt_BR ativo (`locale` mostra LANG=pt_BR.UTF-8)
- [ ] Teclado ABNT2 funciona (digitar `ç`, `~`, `^`)
- [ ] Fuso horário correto (America/Sao_Paulo)
- [ ] Firefox abre
- [ ] LibreOffice abre
- [ ] VLC reproduz vídeo mp4
- [ ] Conexão Wi-Fi funciona via NetworkManager
- [ ] Katu Welcome abre automaticamente
- [ ] Atalho "Instalar Katu OS" está no desktop

### Fase 3 — Instalação (Calamares)

- [ ] Instalador abre sem erros
- [ ] Slideshow aparece durante instalação
- [ ] unpackfs copia o sistema
- [ ] GRUB é instalado corretamente
- [ ] fstab gerado corretamente
- [ ] Usuário e senha definidos funcionam no primeiro boot

### Fase 4 — Sistema Instalado

- [ ] Boot sem pendrive funciona
- [ ] Plymouth aparece no boot instalado
- [ ] Login com usuário criado funciona
- [ ] Katu Welcome abre no primeiro boot (apenas uma vez)
- [ ] `neofetch` ou `hostnamectl` mostra "Katu OS 1.0"
- [ ] `cat /etc/os-release` mostra ID=katu
- [ ] Atualizações via `apt update && apt upgrade` funcionam

### Fase 5 — Hardware Real

- [ ] Hibernação e suspensão funcionam
- [ ] Ajuste de brilho (notebook)
- [ ] Áudio — saída e microfone
- [ ] Câmera (se disponível)
- [ ] USB externo detectado
- [ ] Bluetooth

## Critérios de Aprovação para Release

A ISO está aprovada para release quando:
- Todas as fases 1–4 passam 100% em VirtualBox
- Fase 5 testada em mínimo 2 hardwares diferentes
- Nenhum erro de instalação (Calamares finish sem crash)
- Documento `docs/RELEASE-1.0.md` preenchido com data e assinatura do testador

## Reportar Bugs

Abra uma issue em: https://github.com/katuos/katu-os/issues

Inclua:
1. Versão da ISO (sha256)
2. Hardware ou VM usada
3. Passos para reproduzir
4. Log relevante (`journalctl`, `/var/log/calamares/`)
