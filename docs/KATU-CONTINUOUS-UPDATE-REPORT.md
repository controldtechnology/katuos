# KATU OS — CONTINUOUS UPDATE

Data da auditoria: 29/09/2026. Branch de trabalho: feat/continuous-update-20260928.
Branch publicada: `feat/continuous-update-20260928`.

**Estado: beta assinada publicada; stable e aceitação em máquina instalada ainda
não concluídos.** A beta está disponível para bootstrap e homologação controlada.

Atualizador auditado: GUI Katu Update existente em Python/Qt, evoluída no pacote
existente; backend APT python-apt, Flatpak nativo, Polkit e systemd timer.
Localização e baseline: [auditoria](KATU-UPDATE-AUDIT.md).

| Área | Resultado atual |
|---|---|
| Arquitetura | Implementada; [documentada](updates/ARCHITECTURE.md) |
| Repositório | `https://repo.katuos.com.br`; DNS/TLS ativos; geração publicada no Plesk por symlink atômico |
| Assinatura | Chave GPG de produção criada; fingerprint `402A0557D31BF7402008FB27B658038D520736AC`; privada local cifrada, nunca enviada ao servidor |
| Stable/Beta | stable assinado e vazio; beta assinado publica `katu-update 1.1.1` |
| Componentes | Apps existentes já eram pacotes; assets separados em katu-icons, katu-theme, katu-wallpapers |
| Metapacote | katu-desktop preparado, com Recommends opcionais |
| Update incremental | Exercitado em APT de Debian descartável: somente katu-ai; central permaneceu na versão anterior |
| Repositório público | InRelease de ambos canais, hashes SHA256, gzip e download do `.deb` verificados por HTTPS; `apt-get update` real pendente |
| Dependências | Exercitadas com upgrade katu-core; APT inclui as dependências necessárias |
| Novo aplicativo | Exercitado via metapacote em ambiente descartável |
| Assinatura inválida/corrupção/offline | Rejeitados em testes APT descartáveis |
| Autoatualização | OK no CI Debian descartável: upgrade real do pacote `katu-update` verificado por dpkg e helper |
| Preferências pessoais | Conffiles preservados; migração não percorre /home |
| Histórico/migrações | Estado e histórico APT preparados; idempotência testada |
| Timer/notificações | Unidades e notify-send incluídos; validação de sessão KDE pendente |
| Falhas/espaço/energia | Erros APT, dpkg incompleto, espaço e baixa bateria têm testes |
| ISO atual | Preservada; SHA-256 5078d379640ae4743fe03d78642fde34b040095c36353c7aa30ebd3ee9fb6cda |

Falhas tratadas: dependência impossível é rejeitada pela simulação APT; ausência de
rede, assinatura/payload inválidos, falta de espaço, bateria baixa, pacote retido,
plano alterado e estado dpkg sem validação são reportados como falha. Operações de
boot, base, kernel e instalador permanecem sob mecanismos da distribuição.

Limitações bloqueantes de produção:

1. O subdomínio `repo.katuos.com.br` foi criado no Plesk (ID 3731), com raiz web
   `/var/www/vhosts/katuos.com.br/site1/public` e armazenamento privado em `site1`.
   Em 29/09/2026, o A `repo` → `186.209.113.132` resolve pelo Cloudflare
   (DNS-only). HTTPS validado. Os canais stable/beta e o `.deb` respondem via HTTPS;
   o site raiz sem caminho retorna 403 por não haver índice/listagem. A conta Plesk
   recusou emissão LE pela API CLI e criação de chave API temporária; o certificado
   foi instalado pelo usuário.
2. Não havia VM Katu OS registrada no usuário local, e WSL não está instalado.
   Executar homologação com Katu OS instalado conforme updates/TESTING.md.
3. A chave de produção foi gerada em 29/09/2026 e validada com `gpgv`; fingerprint
   `402A0557D31BF7402008FB27B658038D520736AC`. A passphrase aleatória está cifrada
   pelo DPAPI e a chave privada permanece em AppData com ACL restrita. Publicar o
   fingerprint por canal independente e manter backup cifrado fora desta estação.
4. A transferência de arquivos antes pertencentes a katu-branding e hooks de
   branding precisa de upgrade e remoção testados no Katu OS.
5. A execução CI 36566750249 passou: lintian, testes unitários, 14 integrações
   APT autenticadas (incluindo autoatualização) e smoke test Qt. CI Debian não
   atesta reboot, KDE/Polkit/systemd PID 1 nem hardware.

Próximos passos: validar o repositório com `apt-get update` num Debian/Katu OS;
homologar o bootstrap beta e o upgrade de `katu-update` numa máquina instalada;
preservar um backup cifrado da chave fora desta estação; testar recuperação/remoção;
executar a matriz de stable antes de promover qualquer pacote. O beta público contém
somente o candidato `katu-update 1.1.1` (SHA-256
`f23bd098d4206dd5aacccd14ee06e5d0d1cf960f05254e8d74dd02848e843141`); stable não
contém pacotes.
