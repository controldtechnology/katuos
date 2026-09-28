# Arquitetura de atualização contínua

O pacote `katu-update` e sua GUI Python/Qt continuam sendo o atualizador oficial.
`backend.py` usa python-apt para resolver candidatos, dependências, tamanho e
origem. Uma falha de consulta é um erro, nunca “nenhum update”. APT é a fonte
autoritativa; não há download de ISO nem execução de script remoto.

Fluxo: refresh autenticado → plano com versões e SHA-256 → autorização do usuário
→ Polkit → helper de sistema → serviço transitório systemd → download → instalação
→ consulta dpkg → histórico. O helper recalcula o plano e recusa mudanças desde a
aprovação. Pacotes inalterados não entram na transação; APT reaproveita seu cache.
Não se permitem remoções, downgrades ou violação de holds nesse fluxo normal.

A transação continua no serviço `katu-update-transaction.service` quando o pacote
do próprio updater é substituído. Nenhum postinst reinicia esse serviço ou a GUI.
Cancelamento usa SIGUSR1, aceito somente no download; não sinaliza o dpkg.

Um timer de sistema `katu-update-check.timer` atualiza índices diariamente.
O timer homônimo de sessão lê o resultado e usa notify-send/KDE, com ação VER.
O autostart antigo apenas ativa o timer; a consulta ao update.json foi retirada.

Flatpak mantém remotes e escopos user/system próprios. A GUI mostra origem,
propaga erros e valida ausência das refs atualizadas na consulta posterior.
O histórico administrativo persistente implementado cobre APT; o histórico
completo de Flatpak continua sendo `flatpak history`.

Metapacote: `katu-desktop` depende apenas do núcleo/updater e recomenda os apps.
Recommends ausentes são oferecidos pela GUI para instalação explícita: remover
um aplicativo não faz com que seja reinstalado silenciosamente no próximo update.

Boot, GRUB, Plymouth, Live, Calamares, kernel, drivers e serviços nativos não são
reconfigurados por scripts de cópia. Atualizações críticas continuam usando os
pacotes da distribuição; reboot é sugerido, nunca automático.

## Limites de validação

Contêiner valida APT/dpkg/GPG e Qt offscreen. Não comprova sessão KDE, agente Polkit,
systemd como PID 1, reboot, áudio/rede/hardware ou instalação Calamares. Esses testes
são obrigatórios na máquina Katu de homologação antes de stable.
