# Assinatura

APT autentica InRelease/Release.gpg, os hashes dos índices e os hashes dos .deb.
Sem assinatura válida o refresh falha e a GUI não habilita instalação.
Referência: [apt-secure](https://manpages.debian.org/trixie/apt/apt-secure.8.en.html).

Criar/manter a chave de produção numa estação de release protegida, com backup
cifrado e acesso restrito. Usar passphrase/agente GPG ou hardware apropriado.
GNUPGHOME deve estar fora do Git, ISO, pacotes e document root; nunca exportar
material secreto para o servidor web ou para jobs de teste.

Configuração de release: GNUPGHOME e KATU_SIGNING_KEY (fingerprint completo).
Não são hardcoded. GPG precisa ter acesso ao agente de assinatura. A árvore pública
contém somente a exportação pública ASCII. Testes geram chave descartável em
diretório temporário do contêiner; essa chave nunca é usada em produção.

`configure-client.py` rejeita material privado ASCII e exige exatamente a chave
pública com fingerprint informado. Não baixa chave e confia nela automaticamente.
Para rotação, distribuir primeiro o novo material público por pacote autenticado
com a chave antiga e planejar sobreposição. Revogar após migração dos clientes.
Se a chave antiga for comprometida, tratar como incidente e reprovisionar confiança.

Nenhuma chave de produção foi criada ou publicada durante os testes iniciais.
