# Processo de release

1. Implementar e revisar o componente; incrementar versão e changelog.
2. Testar código, construir .deb e verificar conteúdo/permissões/dependências.
3. Instalar limpo e atualizar da versão anterior em ambiente descartável.
4. Publicar candidato beta assinado na estação de release.
5. Validar em Katu instalado, incluindo remoção e ausência de regressão crítica.
6. Promover exatamente o SHA-256 beta aprovado para stable; não reconstruir o .deb.
7. Publicar árvore pública, validar HTTPS/assinatura e observar Katu Update.

```sh
export GNUPGHOME=/caminho/privado/gnupg
export KATU_SIGNING_KEY=FINGERPRINT_COMPLETO
bash scripts/release/publish-beta.sh output/packages/katu-ai_1.1.0_all.deb --root /srv/katu-release
bash scripts/release/publish-stable.sh output/packages/katu-ai_1.1.0_all.deb --root /srv/katu-release --evidence approval.json
```

approval.json é um registro de revisão local por SHA-256, com booleanos para
build, clean_install, upgrade, functional, dependencies, removal,
no_critical_regression, signature e installed_katu. Anexar referências aos testes,
data e responsável na revisão. A ferramenta exige todos os gates e existência
do mesmo hash no ledger beta. Nunca marcar gate verdadeiro sem evidência.

O CI `continuous-update.yml` compila pacotes e testa em Debian descartável;
artefatos são **candidatos**, não releases stable. Chaves de produção não estão
no job de teste. Build ISO foi tornado manual (`workflow_dispatch`). Alterações
comuns devem acionar o pipeline de componentes, não o de ISO.

`test-package.sh` roda lintian. Warnings existentes precisam ser revisados;
lintian não substitui instalação/upgrade/funcionalidade. Para apps novos, adicionar
Recommends ao metapacote; a GUI oferece instalação explícita. Depends é reservado
ao necessário para funcionamento e aparece no plano para autorização.
