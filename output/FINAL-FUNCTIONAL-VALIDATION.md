# Regressão funcional — reconstrução visual Katu OS

**Estado geral:** pendente para a nova ISO. Nenhum PASS funcional da ISO reconstruída é presumido.

| Verificação | Estado | Evidência/limite |
|---|---|---|
| Testes unitários do repositório | PASS | 12 testes existentes passaram nesta branch |
| Validador de branding Calamares | PASS | `python scripts/validate-installer.py` |
| Compilação sintática Python do Welcome | PASS | `python -m py_compile .../main.py` |
| JSON e XML/SVG dos novos assets | PASS | parsing local de `metadata.json`, `panel-background.svg`, `viewitem.svg` |
| Espelhos do SDDM, Calamares e layout Plasma | PASS | hashes/comparação de arquivo depois da sincronização |
| QML SDDM e slideshow | NOT AUTOMATICALLY VERIFIED | `qmllint`/runtime Plasma e Calamares não disponíveis neste host |
| Boot da ISO reconstruída | NOT RUN | ainda não há ISO nova |
| GRUB/UEFI/BIOS/Live | NOT RUN nesta branch | base dourada preservada em `5ce81b589f5448deedb75b5317609f08c8e955d0`; testes da nova imagem pendentes |
| Abrir Calamares, particionar e instalar | NOT RUN nesta branch | somente `show.qml` e assets de branding mudaram; regressão real ainda necessária |
| Reboot, SDDM, login e desktop instalado | NOT RUN nesta branch | pendente de VM limpa com a nova ISO |

## Proteção da base

- Baseline/tag preservada: `katu-os-golden-master-functional` → `5ce81b589f5448deedb75b5317609f08c8e955d0`.
- Branch isolada: `visual/katu-premium-reconstruction`.
- Não foram alterados scripts de build, kernel, initramfs, parâmetros GRUB, particionamento ou módulos do Calamares. O hook de autostart do Live mudou apenas para apresentar a escolha visual de boas-vindas; precisa de regressão na ISO.
- O layout do painel e temas são configurações de apresentação e ainda necessitam ser exercitados no Plasma da imagem final.
- A interface Live agora apresenta boas-vindas; o botão de instalação chama o wrapper existente `katu-installer`, sem modificar Calamares. As entradas global e de usuário usam o mesmo nome XDG para evitar janelas duplicadas; a inicialização dessa apresentação continua pendente de ISO/VM e não é declarada PASS.
