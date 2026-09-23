# Auditoria de boot — 2026-09-23 (em andamento)

Release bloqueada até concluir a validação. Nenhuma ISO foi reconstruída nesta fase.

## Estado preservado

- HEAD: `8657d0c592209510098f66f56fcf1b4ef9e303d0`, branch `fix/calamares-installation`.
- Único conteúdo não rastreado inicial: `.claude/`. Sem mudanças rastreadas.
- Evidências locais: `output/audit-20260923/` (ignorado pelo Git).
- Último Live documentado: build 35756634827, commit ed2dab6, SHA-256
  `bd8ad41d1cbd43104e04adedc6890c1ea5ab8b63fd9311ab35ee66939f47bc1f`.
  O registro histórico comprova chegada ao desktop, não instalação completa.
- ISO efetivamente usada na VM com falha: Downloads/katu-os-1.0-amd64-iso/katu-os-1.0-amd64.iso,
  3514519552 bytes, SHA-256 `ad5c0564c611057e8dbeed61e38b9f0a1899302c76db615276e90b8af26d3191`.
  Build atual no Actions: 35857262511, HEAD 8657d0c.

## Causa identificada na VM existente

A VM `katuos` NÃO estava inicializando diretamente o conteúdo original da ISO.
O DVD IDE apontava para `Unattended-08211921-6f55-4673-9706-22f0079b6e97-aux-iso.viso`.
Essa mídia importa a ISO, remove `/boot/grub/grub.cfg` e o substitui por um GRUB
gerado pelo modo desassistido do VirtualBox. Todas as linhas `linux` perderam
`boot=live components` e receberam `auto=true preseed/file=/cdrom/preseed.cfg ...
automatic-ubiquity ...`. Até a entrada de diagnóstico foi substituída.

`/proc/cmdline` no BusyBox confirma esses parâmetros e a ausência de `boot=live`.
O GRUB original extraído da ISO contém `boot=live` através de `KATU_BASE`.
Não há evidência de que essa falha específica seja regressão do kernel ou branding.

Diagnóstico executado no initramfs, sem modificar o disco instalado:

- `/dev/sr0` existe; `blkid`: ISO9660, label `KATU_OS_1.0`, UUID `2026-09-23-12-33-00-26`
  (identificação da mídia VISO gerada pelo VirtualBox).
- `mount -t iso9660 -o ro /dev/sr0 /mnt/katu-media`: sucesso.
- `/live/filesystem.squashfs`, kernel e initrd (aliases e nomes versionados) existem.
- SquashFS montado por loop, somente leitura: sucesso.
- `/scripts/live` e `/lib/live/boot/*` presentes, inclusive `9990-main.sh` e overlay.
- `/sbin/init -> ../lib/systemd/systemd`; executável systemd presente no rootfs.
- Erros de vboxvideo coexistem com mídia e SquashFS acessíveis. Não explicam
  a remoção de `boot=live`. Teste gráfico controlado ainda em andamento.

Evidências: `current-vm.png`, `cmdline.png`, `mounts.png`, `Diagnose.png`.
Montagem bem-sucedida não equivale a teste integral de todos os blocos do SquashFS.

## Base comprovada no manifest da ISO atual

| Componente | Versão |
|---|---|
| Base / arquitetura | Debian Trixie / amd64 |
| Kernel | 6.12.107+deb13-amd64 (pacote 6.12.107-1) |
| live-build (log do Actions) | 1:20250505+deb13u1 |
| live-boot / live-boot-initramfs-tools | 1:20250815~deb13u1 |
| live-config / live-config-systemd | 11.0.5 |
| initramfs-tools | 0.148.4 |
| GRUB / EFI / PC | 2.12-9+deb13u2 |
| systemd | 257.13-1~deb13u1 |
| Plasma workspace | 4:6.3.6-2 |
| SDDM | 0.21.0+git20250502.4fe234b-2 |
| Calamares | 3.3.14-1 |

Modelo: Debian Live com initramfs-tools, não Casper. `dracut-install` é ferramenta
auxiliar, não prova de uso de dracut como gerador. Boot configurado com GRUB PC/EFI;
Syslinux/ISOLINUX não é o carregador selecionado.

## Próximas verificações

VM nova `Katu-Audit-20260923`: 4096 MB, 2 CPUs, EFI, VMSVGA, 128 MB, 3D OFF,
DVD SATA com ISO original e VDI novo de 32 GiB. Não reutiliza snapshots.
Live, instalação, boot sem ISO e release final ainda NÃO aprovados.

## Segundo defeito isolado: blacklist gráfica

Com a ISO original a VM nova ultrapassou initramfs, montou overlay e iniciou
systemd/live-config. O SDDM permanecia em `Starting... / Logind interface found`.
`ls /dev/dri` retornou inexistente. O GRUB original incluía
`modprobe.blacklist=vmwgfx`, introduzido no commit da75f66.
No console Live, `sudo modprobe vmwgfx; sudo systemctl restart sddm` fez a tela
gráfica aparecer com VMSVGA e 3D OFF. As mensagens do módulo sobre hypervisor
não impediram esse avanço. Evidências: `driver-test.png`, `driver-result.png`.
Correção focal: retirar blacklist das entradas normais; manter nomodeset apenas
na entrada de compatibilidade. O desktop ainda precisa passar pelos critérios
funcionais; aparecer uma imagem de fundo não é suficiente.

## Continuação: instalação, boot e assets

- O Calamares concluiu a instalação em 23/09 às 13:13:37, com
  `completion: succeeded`, GRUB EFI e fallback `bootx64.efi`.
  Log preservado em `output/audit-20260923/calamares-completed.log`.
- O DVD da VM de auditoria foi esvaziado e a VM iniciou pelo VDI até o SDDM.
  Evidência: `output/audit-20260923/boot-without-iso.png`.
  A tela apresenta problemas visuais; login e desktop instalado ainda não
  foram aprovados. A ISO antiga exigiu carregar vmwgfx manualmente no Live.
- Nove PNGs do Calamares e 20 PNGs de katu-branding/katu-welcome estavam
  corrompidos por conversão binário/texto. A assinatura começava com
  `ef bf bd 50 4e 47`, em vez de `89 50 4e 47 0d 0a 1a 0a`.
  Restaurados de versões válidas do histórico Git, sem recriar o design.
  Preflight e validador do instalador passam a verificar assinatura,
  integridade CRC dos chunks e término dos PNGs.
- Build Actions `35887374645` (commit e97f234) falhou no smoke QEMU após
  os 11 checks estruturais passarem. O serial registra falha do serviço
  katu-qa-live, sem marcador PASS nem diagnóstico suficiente para atribuir
  causa. Evidências baixadas em `output/audit-20260923/actions-evidence/`.
  O helper agora envia erros e diagnóstico do SDDM ao serial; o runner
  rejeita imediatamente um marcador FAIL e usa os parâmetros do GRUB real.
- Os 12 testes locais de regressão passaram, incluindo corrupção PNG e
  bloqueio de release por evidência ausente/incompatível. A configuração
  do instalador também passou na validação local.

As correções locais ainda precisam de uma nova ISO e novos testes Live,
instalação, desktop e boot sem mídia para o SHA-256 dessa ISO. Não houve
publicação de release. USB físico continua NOT TESTED.
