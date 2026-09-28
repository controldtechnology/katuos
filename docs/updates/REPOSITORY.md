# Repositório APT

Produção: `https://repo.katuos.com.br`. A URL é configurável no bootstrap.
Suites independentes: stable e beta; componente main; amd64 e pacotes all.
`scripts/release/repository.py` usa apt-ftparchive e GnuPG, sem formato proprietário.

```text
armazenamento-privado/
  generations/release-.../
    pool/main/*.deb
    dists/stable/{InRelease,Release,Release.gpg,main/binary-amd64/Packages*}
    dists/beta/{InRelease,Release,Release.gpg,main/binary-amd64/Packages*}
    katu-archive-keyring.asc
    ledger.json
  public -> generations/release-...
```

Somente `public` é document root do subdomínio. A chave privada fica fora de todo
esse armazenamento. Publicação troca o symlink atomicamente, retém versões antigas
do pool e não reutiliza um nome/versão com bytes diferentes. Metadata expira após
14 dias; renovar as assinaturas antes do vencimento mesmo sem novos pacotes.
`ledger.json` serve à promoção no release host, nunca à decisão de instalar no cliente.

Servidor observado em 28/09/2026: conta Plesk em CageFS, sem CLI administrativa,
sem dpkg-deb/apt-ftparchive. DNS de repo.katuos.com.br ainda ausente na verificação.
Build/signing precisam ocorrer em host Debian separado. Configurar DNS, vhost e
certificado TLS no painel antes do deploy. Não apontar para o httpdocs do site atual.

Deploy: `scripts/release/deploy-repository.sh PUBLIC_GENERATION`. Configurar
KATU_DEPLOY_HOST (alias SSH), KATU_DEPLOY_ROOT, KATU_SSH_PORT e KATU_VERIFY_KEYRING.
Host key SSH deve ser verificada. O script transfere somente a árvore pública e
verifica as assinaturas antes de transferir. Banco de dados não é utilizado.

## Bootstrap de uma instalação já existente

A ISO atual não contém chave/sources do repositório novo. Isso impede o updater
antigo de descobrir o primeiro pacote por APT sem provisionamento de confiança.
É necessário um bootstrap administrativo único; isso **não exige nova ISO**.

Distribuir a chave pública e conferir seu fingerprint por canal confiável.
Executar o script local revisado:

```sh
sudo python3 scripts/release/configure-client.py \
  --key katu-archive-keyring.asc --fingerprint FINGERPRINT_COMPLETO \
  --url https://repo.katuos.com.br --channel stable
sudo apt-get -o APT::Update::Error-Mode=any update
sudo apt-get install katu-update katu-desktop
```

Antes disso, auditar fontes deixadas pela mídia; desativar a fonte local de build
se ela apontar para diretório inexistente. Nunca adicionar trusted=yes para contornar
o bootstrap. O script salva configuração anterior quando substitui seu próprio
arquivo, valida URL HTTPS e fingerprint, e configura Signed-By dedicado.
