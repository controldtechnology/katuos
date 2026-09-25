# Validação funcional da candidata visual Katu OS

**Estado: validação funcional parcial concluída; ainda não é aprovação para produção.** Os testes abaixo foram feitos na ISO exata de SHA-256 `f6f0fddb170e63c0c0555d0f5979946c1cf14f16c08fccc657f08ef587aa32ca`, build do commit `48223e8`.

| Verificação | Resultado | Evidência / limite |
|---|---|---|
| Build e validação estrutural da ISO | PASS | CI run `36129854861`; 11 verificações estruturais, BIOS/UEFI e QEMU Live smoke passaram. |
| GRUB e boot da ISO | PASS | Candidata iniciou na VM separada de QA em modo BIOS/Legacy. |
| Live e desktop Plasma | PASS | Desktop Live abriu em VirtualBox VBoxSVGA, 1024×768. |
| Welcome no Live | PASS | Uma janela visível; correção da duplicidade confirmada visualmente. |
| Iniciar Calamares | PASS | Instalador abriu em português brasileiro. |
| Navegação e configuração de instalação | PASS | Localização, teclado, disco-alvo, usuário e resumo percorridos. Disco QA vazio de 32 GiB foi o único alvo. |
| Instalação | PASS | Calamares mostrou “Katu OS 1.0 foi instalado no seu computador” e habilitou Concluído. |
| Reinício e boot sem ISO | PASS | ISO ejetada, ordem definida para disco; sistema instalado iniciou em BIOS/MBR. |
| SDDM e autenticação | PASS | SDDM apresentou o usuário de teste; credenciais configuradas apenas para esta VM autenticaram com sucesso. |
| Desktop instalado | PASS | Plasma carregou wallpaper oficial e Welcome de primeiro acesso; Welcome fechou sem bloquear a sessão. |
| Menu Katu | PASS | Launcher abriu com busca, favoritos, categorias e opções de energia. |
| Calamares em UEFI | NOT TESTED | Validação estrutural UEFI passou, mas instalação manual foi apenas em BIOS/Legacy. |
| Resoluções e escala ampliada | NOT TESTED | QA visual desta VM ocorreu em 1024×768; não generalizar para outras resoluções/escalas. |
| Dolphin, Settings, notificações, lockscreen | NOT TESTED nesta instalação | Não foram percorridos individualmente após login. |

## Capturas reais

As capturas estão em `output/FINAL-VISUAL-QA/`:

- `candidate-48223e8-boot.png`, `candidate-one-welcome.png`: boot Live e Welcome sem duplicidade.
- `candidate-calamares-start.png`, `candidate-calamares-step.png`, `candidate-calamares-user.png`, `candidate-calamares-confirm.png`, `candidate-calamares-progress.png`: páginas do instalador, resumo e progresso.
- `install-progress-10.png`: tela de conclusão do Calamares.
- `installed-login-result-2.png`: desktop instalado com Welcome de primeiro acesso.
- `installed-desktop-clean.png`: desktop sem janelas.
- `installed-launcher.png`: menu Katu aberto.

## Observações

- A sessão SDDM/Plasma iniciou e autenticou, mas a tela de login apareceu clara e genérica em vez da composição Katu esperada. Esse é um defeito visual observado, não uma falha de autenticação.
- A interface principal do Calamares mostrou slides oficiais e sidebar Katu, mas a área de conteúdo permaneceu clara/genérica. O fluxo funcional foi concluído.
- Não foram executados testes de instalação em UEFI, escalas, múltiplas resoluções ou todas as aplicações. Não declarar esses cenários aprovados.
- A Golden Master funcional permanece intacta na tag `katu-os-golden-master-functional` (`5ce81b589f5448deedb75b5317609f08c8e955d0`).
