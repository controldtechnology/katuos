# Build e aprovação da ISO

`sudo bash scripts/build.sh` usa uma árvore nova em `build/clean-DATA-COMMIT`.
Não reutiliza kernel, initrd, SquashFS ou cache de uma execução anterior, nem
sobrescreve as ISOs antigas. A árvore pode ser removida depois da auditoria;
não é necessário apagar evidências para obter uma build limpa.

Ordem obrigatória: preflight de fontes → testes de regressão → bootstrap →
chroot → preflight do chroot → binary → validação da própria ISO → QEMU Live →
checksum/manifest da candidata. Uma falha interrompe a execução.

O validador descompacta todo o SquashFS, confere init/systemd, referências GRUB,
versão real do kernel, todos os membros CPIO do initrd, drivers e scripts Live,
instalador, branding, catálogo BIOS/UEFI e estrutura híbrida. Precisa de Linux,
Python 3, xorriso, squashfs-tools, initramfs-tools-core, zstd/lz4/cpio,
grub-common, mtools e espaço temporário para ISO + rootfs descompactado.

O smoke QEMU usa o kernel/initrd extraídos da ISO final e a ISO como CD-ROM.
Só passa com confirmação emitida pelo próprio convidado de systemd, SDDM,
Plasma registrado no DBus e rootfs overlay. Não testa o firmware/GRUB nem
substitui os testes de interação, instalação e boot do disco.

Nenhuma build CI publica release automaticamente. Após os testes manuais,
fornecer um JSON com `sha256` da ISO e `tests` contendo:

- `VIRTUALBOX LIVE`, `VIRTUALBOX INSTALLATION`, `BOOT WITHOUT ISO`, `BRANDING`:
  objetos com `status: "PASS"` e `evidence` apontando para logs/capturas.
- `PHYSICAL USB`: status explícito; sem hardware usar
  `NOT TESTED — requires physical hardware`.

Executar `python3 scripts/release-gate.py ISO --manual RESULTADOS.json
--commit COMMIT --build-date DATA`. O script exige relatórios automatizados
aprovados para o mesmo SHA-256. Nunca reaproveitar aprovações de outra ISO.

## VirtualBox

Criar VM sem instalação desassistida e conectar a ISO original diretamente ao
DVD. A opção **Pular instalação desassistida / Skip Unattended Installation**
evita que o VirtualBox substitua o GRUB por parâmetros de preseed incompatíveis
com Debian Live. A instalação do Katu é guiada pelo Calamares no desktop.
O helper `scripts/test-vbox.ps1` cria uma VM de auditoria sem executar unattended.
Ele é ferramenta desta auditoria, com nome e diretório de evidências próprios.

Não adicionar drivers proprietários ou alterar o kernel para resolver o VISO.
Não voltar a bloquear vmwgfx nas entradas normais: VMSVGA precisa desse driver.

## Reprodutibilidade

O processo é único para CI e build local; SOURCE_DATE_EPOCH vem do commit.
Manifest registra versões, commit, tamanho, label e SHA-256. Os mirrors APT e
downloads de terceiros existentes ainda são móveis: isso NÃO garante ISO
idêntica byte a byte em datas diferentes. Uma release reproduzível byte a byte
exige também congelar/reter todos os pacotes e downloads por hash.
