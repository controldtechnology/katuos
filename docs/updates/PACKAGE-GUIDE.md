# Guia de pacotes

Fonte: `packages/<nome>/`, payload com caminhos Linux e `DEBIAN/control`,
`DEBIAN/changelog`, scripts de mantenedor quando necessários. Criar um app em
`apps/katu-novo-app` é permitido, mas seu artefato final deve ser um pacote Debian
declarado em `packages/`; não criar um instalador paralelo.

Versão: MAJOR.MINOR.PATCH. PATCH corrige; MINOR adiciona funcionalidade compatível;
MAJOR introduz incompatibilidade. A versão em control é autoritativa. Atualize o
changelog na mesma alteração. O builder recusa divergência e sobrescrita do .deb.
Versões legadas 1.0/1.0-1 passam a 1.0.2; apps já em 1.0.1 ficam nessa versão se
seu payload não mudar. Cada futura alteração exige incremento apenas de seu pacote.

```sh
bash scripts/release/build-package.sh katu-ai --output output/packages
bash scripts/release/test-package.sh output/packages/katu-ai_1.1.0_all.deb
```

O builder normaliza LF/permissões, gera conffiles para `/etc` e instala changelog
em `/usr/share/doc/<pacote>/changelog.Debian.gz`. Nunca incluir /home ou chaves.
`X-Katu-Notes` e `X-Katu-Category` no control aparecem no índice APT autenticado
e na GUI. Categorias: Segurança, Correção, Melhoria, Nova funcionalidade,
Aplicativo, Sistema e Visual. Changelog deve listar mudanças, correções e migrações.

Use Depends para requisitos técnicos reais (ex.: `katu-core (>= 1.4.0)`),
Recommends para apps opcionais do desktop, Suggests para integrações opcionais.
Breaks/Replaces descrevem transferência de arquivos; não usar Conflicts de forma
genérica. Provides só se houver compatibilidade real com uma interface virtual.

## Fronteiras dos componentes

Apps existentes permanecem independentes: core, central, ai, store, update,
welcome, drivers, connect, backup, webapps, help, diagnostic, feedback, ia, xampp.
Branding passa a depender dos pacotes de assets para uma transição atômica de
propriedade. Ícones, wallpapers e tema podem receber versões próprias depois.
`katu-desktop-defaults` é compatibilidade sobre `katu-default-settings`; não duplica
arquivos. Não há app katu-security novo: UFW e segurança da base continuam nativos.

Os assets atuais de `config/includes.chroot/usr/share` são incorporados pelo
builder aos respectivos pacotes de ícones, wallpapers, tema e branding. Editar
essas fontes exige incrementar o pacote proprietário. Não reintroduzir arquivo
com o mesmo caminho em dois pacotes. Layouts existentes do usuário não são resetados.
