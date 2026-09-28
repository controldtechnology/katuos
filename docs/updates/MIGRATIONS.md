# Migrações

`packages/katu-update/usr/lib/katu-update/migrate.py` registra migrações numeradas
em `/var/lib/katu-update/migrations/`. O marcador só é persistido após conclusão,
com escrita temporária, fsync e rename. Reexecução não repete migração concluída.
A migração 001 inicializa o estado da infraestrutura; não modifica perfis pessoais.

Cada componente que alterar schema deve adicionar migração versionada ao seu
próprio pacote: verificar versão antiga, fazer backup apropriado, transacionar,
validar e registrar. Testar repetição, falha antes/depois da escrita e upgrade
desde a versão suportada. Não importar scripts de internet para executar como root.

Transferência de assets usa Breaks/Replaces e Depends coordenados no branding.
O dpkg preserva conffiles modificados; instalação usa --force-confold. Defaults
de sistema vivem em /etc/xdg ou /usr/share; não reescrever ~/.config e /home.
