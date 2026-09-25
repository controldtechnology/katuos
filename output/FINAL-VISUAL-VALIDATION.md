# QA visual final — candidata `48223e8`

**Resultado: parcial; não aprovada como visual premium final.** A inspeção da ISO em VirtualBox foi feita em BIOS/Legacy, VBoxSVGA, 1024×768. A ISO testada tem SHA-256 `f6f0fddb170e63c0c0555d0f5979946c1cf14f16c08fccc657f08ef587aa32ca`.

| Área | Resultado observado |
|---|---|
| Live e wallpaper | PASS visual em 1024×768; arte oficial Katu visível. |
| Welcome Live | PASS; apenas uma janela após a correção da duplicidade. |
| Painel | PASS básico; painel inferior e ícones visíveis. |
| Launcher | PASS básico; busca, favoritos, categorias e energia visíveis no menu Katu. |
| Calamares | Parcial; branding/sidebar Katu e slides oficiais aparecem, layout cabe em 1024×768, mas conteúdo claro permanece genérico. |
| SDDM | Parcial; apareceu e aceitou login, porém visual claro/genérico e teclado virtual destoam do tema Katu. |
| Desktop instalado | PASS básico; wallpaper e Welcome Katu aparecem; Welcome fechável. |
| Lockscreen | NÃO VALIDADO como experiência final. A tela de bloqueio automática do Live não basta para aprovar. |
| Dolphin, Configurações, notificações e calendário | NÃO TESTADOS individualmente. |
| Resoluções/escala | Só 1024×768 foi observado. Restantes não testados. |

Capturas: `output/FINAL-VISUAL-QA/` — `candidate-48223e8-boot.png`, `candidate-one-welcome.png`, `candidate-calamares-*.png`, `install-progress-10.png`, `installed-login-result-2.png`, `installed-desktop-clean.png` e `installed-launcher.png`.

Não marcar 1280×720, 1366×768, 1600×900, 1920×1080, 2560×1440 ou escalas 125–200% como aprovados: não foram executados. É necessário refinar o tema do SDDM e a área clara do Calamares para cumprir a meta premium; não foi feita mudança funcional para contornar isso.
