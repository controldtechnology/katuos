# QA visual final — em andamento

**Não aprovado para release.** A branch visual ainda não foi empacotada em uma nova ISO, e a nova sessão Plasma/SDDM não foi iniciada.

## Captura da ISO funcional anterior

- VM: `Katu-Audit-20260923`, VirtualBox, controladora VboxSVGA.
- ISO montada: `C:\katuos\output\manual-review-35980066932\candidate-20260924T091825Z-5ce81b58\katu-os-1.0.1-rc1-amd64.iso`.
- Resolução da captura: `1024x768`.
- Evidência: [00-current-iso-1024x768.png](FINAL-VISUAL-QA/00-current-iso-1024x768.png).
- Resultado visível: wallpaper e marca aparecem, mas não há campo de senha nem botão de entrada na captura.
- Causa encontrada no código dessa base: `sddm/katu/Main.qml` fixa `1920x1080`; em 1024x768, o conteúdo de autenticação pode ficar fora da área renderizada.

## Alterações visuais aguardando captura

| Tela | Mudança feita | Captura nova | Status |
|---|---|---|---|
| SDDM | composição responsiva, arte oficial, logo, formulário e ações preservadas | pendente | não validado |
| Desktop/painel | painel inferior flutuante, centralizado, 56 px e com ícone Katu | pendente | não validado |
| Plasma | tema SVG Katu, esquema KatuDark derivado das artes | pendente | não validado |
| Dolphin/Settings/notificações | herdam o esquema do KDE e partes do Plasma Style | pendente | não validado |
| Calamares | seis pôsteres oficiais inteiros, proporção preservada | pendente | não validado |
| Welcome | arte oficial em layout editorial, ações atuais preservadas | pendente | não validado |
| Plymouth | marca, spinner e pontos oficiais | pendente | não validado |
| Lockscreen | nenhuma mudança nesta etapa | pendente | não validado |
| GRUB | logo e seleção oficiais substituem os protótipos; entradas e parâmetros intactos | pendente | não validado |

## Matriz de resolução e escala

`1024x768`, `1280x720`, `1366x768`, `1600x900`, `1920x1080`, `2560x1440` e escalas `100%`, `125%`, `150%`, `175%`, `200%`: **NOT AUTOMATICALLY VERIFIED**. A única captura disponível é da ISO anterior em 1024×768. Não marcar como aprovado até capturar a ISO nova em cada cenário possível.
