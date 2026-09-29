# KATU OS — CONTINUOUS UPDATE

Data da auditoria: 29/09/2026. Branch de trabalho: feat/continuous-update-20260928.
Branch publicada: `feat/continuous-update-20260928`.

**Estado: infraestrutura de código e testes preparada; produção e aceitação em
máquina instalada ainda não concluídas.** Não anunciar atualização contínua em
produção antes de concluir os itens abaixo e revisar o CI final.

Atualizador auditado: GUI Katu Update existente em Python/Qt, evoluída no pacote
existente; backend APT python-apt, Flatpak nativo, Polkit e systemd timer.
Localização e baseline: [auditoria](KATU-UPDATE-AUDIT.md).

| Área | Resultado atual |
|---|---|
| Arquitetura | Implementada; [documentada](updates/ARCHITECTURE.md) |
| Repositório | Gerador assinado preparado; vhost Plesk criado; DNS público ainda não resolve |
| Assinatura | GPG/apt-secure exercitados com chave descartável; chave de produção ausente |
| Stable/Beta | Geração e gate de promoção preparados; nenhum canal de produção publicado |
| Componentes | Apps existentes já eram pacotes; assets separados em katu-icons, katu-theme, katu-wallpapers |
| Metapacote | katu-desktop preparado, com Recommends opcionais |
| Update incremental | Exercitado em APT de Debian descartável: somente katu-ai; central permaneceu na versão anterior |
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
   O A `repo` → `186.209.113.132` já resolve pelo Cloudflare (DNS-only). HTTPS
   ainda apresenta certificado de nome incorreto. A conta Plesk recusou tanto a
   emissão LE via CLI quanto a criação de uma chave API temporária (permissão negada).
   A emissão precisa ser feita no painel por uma conta com essa permissão ou por
   administrador Plesk. Sem TLS válido e chave de assinatura de produção, nada foi publicado.
2. Não havia VM Katu OS registrada no usuário local, e WSL não está instalado.
   Executar homologação com Katu OS instalado conforme updates/TESTING.md.
3. Nenhuma chave de assinatura de produção foi provisionada. Criar/recuperar a
   chave fora do Git, ISO, CI e raiz pública; distribuir fingerprint por canal
   independente.
4. A transferência de arquivos antes pertencentes a katu-branding e hooks de
   branding precisa de upgrade e remoção testados no Katu OS.
5. A execução CI 36563783648 passou: lintian, testes unitários, 14 integrações
   APT autenticadas (incluindo autoatualização) e smoke test Qt. CI Debian não
   atesta reboot, KDE/Polkit/systemd PID 1 nem hardware.

Próximos passos: emitir e validar TLS com conta Plesk autorizada; obter chave de assinatura por processo protegido;
homologar bootstrap de confiança
em instalação existente; obter chave por processo protegido; executar a matriz beta
no Katu OS instalado; anexar evidências por SHA-256; só então publicar beta, promover
stable e testar a notificação/atualização real. Nenhum pacote foi publicado no site;
nenhuma chave de produção foi criada.
