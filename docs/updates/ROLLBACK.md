# Recuperação e rollback

Não existe garantia de rollback completo neste projeto. O filesystem da máquina
instalada e sua política de snapshots ainda precisam ser auditados. Não criar
snapshots fictícios nem chamar downgrade de rollback de dados.

APT mantém cache e logs nativos; o repositório retém versões anteriores. Um
downgrade controlado exige revisão de schemas, dependências e conffiles, backup
e autorização administrativa. A GUI normal recusa downgrade/removal.

Após queda de energia durante dpkg, a operação pode ficar incompleta. Consultar
`dpkg --audit`, `/var/log/dpkg.log`, `/var/log/apt/history.log` e o estado/histórico
do Katu Update. Um administrador deve revisar antes de `dpkg --configure -a` e
`apt-get -f install`; não executar reparação automática que remova pacotes.

A ISO preservada continua sendo mídia de recuperação. Kernel anterior, se mantido
pela distribuição, pode ser escolhido no GRUB. Não remover kernels automaticamente.

Offline updates: PackageKit/systemd oferecem infraestrutura nativa, mas não havia
integração no updater auditado. Não ativamos /system-update nem reboot offline sem
validar backend, serviço e recuperação na instalação. Referência:
[PackageKit offline](https://github.com/PackageKit/PackageKit/blob/main/docs/offline-updates.txt).
