# Katu OS APT Repository

Destino oficial: https://repo.katuos.com.br, suites stable e beta.

Consulte [configuração e bootstrap](../docs/updates/REPOSITORY.md),
[assinatura](../docs/updates/SIGNING.md) e
[processo de release](../docs/updates/RELEASE-PROCESS.md).

`setup-repo.sh` é um ponto de entrada compatível para o publicador autenticado:

```sh
bash repository/setup-repo.sh publish beta output/packages/katu-ai_1.1.0_all.deb --root /srv/katu-release
```

Exige GNUPGHOME privado e KATU_SIGNING_KEY configurados. O host de assinatura
não é o servidor web. Somente a geração pública deve ser hospedada.
Nunca usar trusted=yes ou desabilitar validação de assinatura no cliente.
