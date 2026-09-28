# Auditoria Katu Update — 28/09/2026

Baseline Git: `3d4521f588d60b397e3125ba33164613825582d1`.
Antes da intervenção não havia alterações rastreadas; `.claude/`, `dist/`,
`worktrees/` e `--help` eram não rastreados e não pertencem à intervenção.
ISO preservada: `dist/run-36410706498/candidate-20260928T103901Z-3d4521f5/katu-os-1.0.1-rc1-amd64.iso`.
SHA-256 medido: `5078d379640ae4743fe03d78642fde34b040095c36353c7aa30ebd3ee9fb6cda`.

## Implementação encontrada

* GUI: `packages/katu-update/usr/lib/katu-update/main.py`, Python, PyQt5,
  fallback PySide6; launcher `usr/bin/katu-update`. Não roda inteira como root.
* Backend compartilhado: `packages/katu-core/usr/lib/python3/dist-packages/katu_core/packages.py`.
  Executa `pkexec apt-get update`, `upgrade -y` e simulação de upgrade.
* A listagem extrai a versão instalada, não a candidata. Erros viram lista vazia.
  A GUI ignora falha do refresh; falha de Flatpak não altera resultado final.
* Flatpak: `remote-ls --updates`; instalação via `flatpak update --noninteractive`.
* PackageKit: nenhuma integração do updater. Discover/Flatpak está na lista de
  pacotes da imagem. Não foi comprovado suporte offline na instalação real.
* Polkit: `pkexec` para comandos administrativos; sem ação específica do updater.
* systemd: unidades **de usuário** em `packages/katu-update/usr/lib/systemd/user/`.
  O serviço executa `apt-get update` sem root e notifica mesmo após falha.
  postinst tenta habilitar só para usuários existentes e ignora falhas.
* Notificações: `notify-send` via katu_core; KDE usa seu serviço nativo.
* Checker duplicado: `config/includes.chroot/usr/lib/katu/katu-update-check`,
  autostart global, consulta `https://katuos.com.br/update.json`, compara strings
  de versão e anuncia link de download. Não é fonte confiável para APT.
* `repository/setup-repo.sh`: só quatro pacotes, versão 1.0 fixa, sem assinatura,
  exemplo `trusted=yes`, suite `katu`, criação de pool incompleta.
* Build ISO: `scripts/build-clean.sh` constrói todos os diretórios `packages/`,
  adiciona repositório **local de build** confiado, copia assets e executa hooks.
  CI gerava ISO em todo push. Nenhum repositório público autenticado é provisionado
  ao cliente por esse código. Sources reais precisam ser examinadas na instalação.

## Componentes

Já empacotados: katu-ai, backup, branding, central, connect, core,
default-settings, diagnostic, drivers, feedback, help, ia, installer,
release, store, update, webapps, welcome, xampp. Versões misturam 1.0,
1.0-1 e 1.0.1. Aplicativos já são unidades de atualização independentes.

Branding contém logos, ícones hicolor, wallpapers e uma paleta. Plasma,
SDDM, Plymouth, GRUB, configurações KDE, segurança, configuração do Live,
serviços e instalador também são copiados/gerados por includes/hooks.
Separar assets de desktop é apropriado; não transferir boot/instalador para
simples scripts de cópia de atualização. `katu-security` não é um app existente:
UFW e os hooks de segurança não devem virar um pacote vazio com promessa falsa.
`katu-default-settings` mantém o nome para preservar dependências existentes.

## Ambiente observado

Windows, Python 3.13 disponível em Laragon, WSL ausente. VirtualBox não listou
VMs neste usuário. Não equivale a teste num Katu OS instalado.
SSH do servidor Plesk funciona como usuário de hospedagem; Linux com Python/GPG,
sem dpkg-deb/reprepro no PATH observado. Banco de dados não é necessário.
Credenciais não fazem parte deste relatório.

## Decisão

Evoluir a mesma GUI e pacote. APT/python-apt resolve versões, dependências e
confiança; serviço root transitório mantém transação independente da GUI.
Flatpak preserva seus remotes. Um timer de sistema atualiza índices e um timer
de sessão consulta resultados e notifica. Distribuição em stable/beta assinados,
sem versão remota de ISO como fonte técnica. Bootstrap de confiança para ISOs
antigas é necessário uma única vez, sem reconstrução da ISO.

Referências: [apt-secure](https://manpages.debian.org/trixie/apt/apt-secure.8.en.html),
[offline PackageKit](https://github.com/PackageKit/PackageKit/blob/main/docs/offline-updates.txt).
