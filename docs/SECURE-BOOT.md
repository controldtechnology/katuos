# Katu OS — Secure Boot

## Status no Katu OS 1.0

O Katu OS 1.0 **não assina o bootloader** — Secure Boot deve estar desabilitado para instalar.

Isso é padrão para distribuições independentes sem chave MOK registrada na Microsoft.

## Como Desabilitar Secure Boot

1. Reinicie o computador
2. Entre no BIOS/UEFI (`Del`, `F2`, ou `F10`)
3. Encontre **"Secure Boot"** em Security ou Boot
4. Mude para **"Disabled"**
5. Salve e reinicie

## Verificar se Secure Boot está ativo (no Linux)

```bash
mokutil --sb-state
# "SecureBoot disabled" — OK para instalar Katu OS
# "SecureBoot enabled"  — desabilitar antes de instalar
```

## Roteiro para Suporte Secure Boot (v2.0)

Para versões futuras, o caminho é:

1. Gerar chave MOK (Machine Owner Key):
   ```bash
   openssl req -new -x509 -newkey rsa:2048 -keyout MOK.key -out MOK.crt \
     -days 3650 -subj "/CN=Katu OS Secure Boot/"
   openssl x509 -in MOK.crt -out MOK.cer -outform DER
   ```

2. Assinar o GRUB:
   ```bash
   sbsign --key MOK.key --cert MOK.crt \
     /boot/efi/EFI/katuos/grubx64.efi \
     --output /boot/efi/EFI/katuos/grubx64.efi
   ```

3. Assinar o kernel:
   ```bash
   sbsign --key MOK.key --cert MOK.crt \
     /boot/vmlinuz-* --output /boot/vmlinuz-*
   ```

4. Registrar a chave MOK via `mokutil --import MOK.cer`

5. Habilitar assinatura automática via DKMS para módulos de kernel

## Alternativa: Usar shim

A abordagem preferida é usar o shim da Debian (que tem chave Microsoft), 
o que permite boots sem registrar MOK manualmente.

```
shim-signed → grubx64.efi → vmlinuz → initrd → Katu OS
```

Isso requer:
- Pacote `shim-signed` do Debian
- Configuração do GRUB para carregar via shim
- Teste em hardware real com Secure Boot habilitado

Planejado para Katu OS 2.0.
