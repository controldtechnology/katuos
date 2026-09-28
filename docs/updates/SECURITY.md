# Segurança operacional

GUI sem root; helper fixo autenticado por Polkit, sem senha armazenada. O serviço
root usa arquivos de estado em /var/lib/katu-update e comandos com argumentos em
lista. Plano é recalculado no root e vinculado às versões/hash dos pacotes.

APT recusa pacotes não autenticados; Signed-By limita a chave do repositório Katu.
Não há botão para ignorar assinatura. Sem curl|bash, scripts remotos, ISO de update,
sobrescrita de /home ou reinício automático. O download pode ser cancelado, dpkg não.
Holds, downgrades e remoções são recusados no plano. Espaço e bateria são verificados
antes da operação; em baixa bateria uma atualização crítica exige conectar energia.

Logs Katu armazenam fase, pacote, versão, progresso e erros de alto nível. Não
persistem saída bruta de comandos ou URLs que possam conter credenciais. APT/dpkg
mantêm seus logs nativos. Secrets não pertencem a control, changelog, Git ou .deb.

Transações concorrentes Katu são bloqueadas por lock; locks APT/dpkg continuam
autoritativos. Mudança do plano durante download aborta antes da instalação.
Testes destrutivos/interrupções devem ocorrer apenas em convidados descartáveis.
