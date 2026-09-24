# Katu OS — Golden Baseline Funcional

## Registro de preservação

- **Branch congelada:** `baseline/katu-os-functional`
- **Tag:** `katu-os-golden-functional`
- **Commit preservado:** `5ce81b589f5448deedb75b5317609f08c8e955d0`
- **Branch de evolução visual:** `visual/katu-brand-identity`
- **Versão indicada pelo projeto:** `1.0.1-rc1`
- **ISO candidata preservada:** `output/manual-review-35980066932/candidate-20260924T091825Z-5ce81b58/katu-os-1.0.1-rc1-amd64.iso`
- **Tamanho:** 3.514.912.768 bytes
- **SHA-256:** `6d992b91b5978a4cd61d8bf82942405f577ca0501409c784755c46fccfea6dfd`

A baseline Git protege o conteúdo rastreado no commit acima. A ISO já existente permanece como arquivo separado e não será sobrescrita. O checkout inicial também continha arquivos não rastreados (`.claude/`, `--help` e `docs/AUDITORIA-VISUAL-IDENTIDADE-KATU-OS.md`); eles foram deixados intactos e não fazem parte da tag.

## Estado funcional registrado

O responsável pelo projeto declarou como funcional o boot da ISO, GRUB, Live, instalador, instalação em disco, inicialização pós-instalação e login. Capturas e relatórios antigos no workspace são históricos e não substituem uma nova regressão da ISO final. A confirmação integral de todos os cenários no build visual permanece **NOT AUTOMATICALLY VERIFIED** até a validação final descrita em `output/KATU-ISO-VALIDATION.md`.

## Arquivos protegidos e inventário

O manifesto [`KATU-GOLDEN-FUNCTIONAL.sha256`](KATU-GOLDEN-FUNCTIONAL.sha256) registra os hashes SHA-256 de 178 arquivos de `scripts/`, `config/`, `grub/`, `installer/calamares/modules/` e `installer/calamares/settings.conf`. Ele inclui scripts de build e validação, configuração de live-build, hooks, listas de pacotes, entradas de boot e configuração do instalador.

As listas declaradas de pacotes estão preservadas, sem modificação, em [`KATU-GOLDEN-PACKAGES.txt`](KATU-GOLDEN-PACKAGES.txt). A estrutura de boot permanece descrita nos arquivos `config/bootloaders/grub-efi-amd64/grub.cfg` e `config/bootloaders/grub-pc/grub.cfg`; os parâmetros de live-build estão em `config/live-build.conf`. A configuração técnica do Calamares está em `installer/calamares/settings.conf` e `installer/calamares/modules/`.

## Regra de trabalho

As mudanças desta evolução ficam na branch visual. Boot, kernel, initramfs, systemd, live-build, criação do usuário Live, montagem, SquashFS, parâmetros de boot, GRUB funcional, hooks funcionais e módulos/fluxos técnicos do Calamares ficam protegidos. Cada arquivo proposto será classificado antes da edição. A configuração e os assets puramente visuais podem mudar; se não for possível separar a apresentação da lógica, a mudança fica pendente e não será feita automaticamente.

Antes de uma ISO nova, comparar o manifesto da baseline com o checkout e explicar toda diferença. A versão anterior e sua SHA-256 permanecem como fallback.
