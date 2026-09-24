# QA visual final — em andamento

**Não aprovado para release.** A branch visual ainda não foi empacotada em uma nova ISO, e a nova sessão Plasma/SDDM não foi iniciada.

## Captura da ISO funcional anterior

- VM: `Katu-Audit-20260923`, VirtualBox, controladora VboxSVGA.
- ISO montada: `C:\katuos\output\manual-review-35980066932\candidate-20260924T091825Z-5ce81b58\katu-os-1.0.1-rc1-amd64.iso`.
- Resolução da captura: `1024x768`.
- Evidência: [00-current-iso-1024x768.png](FINAL-VISUAL-QA/00-current-iso-1024x768.png).
- Resultado visível: wallpaper e marca aparecem, mas não há campo de senha nem botão de entrada na captura.
- Causa encontrada no código dessa base: `sddm/katu/Main.qml` fixa `1920x1080`; em 1024x768, o conteúdo de autenticação pode ficar fora da área renderizada.
- Captura repetida após o usuário iniciar a VM: confirmou o mesmo defeito; `user-vm-current.png` é evidência local adicional, da mesma ISO Golden Master.
- Uma VM separada de QA mostrou “Please insert a bootable medium” porque estava sem controlador/mídia conectada. Ela foi desligada; essa tela não é evidência sobre o boot da ISO.

## Alterações visuais aguardando captura

| Tela | Mudança feita | Captura nova | Status |
|---|---|---|---|
| SDDM | composição responsiva, arte oficial, logo, formulário e ações preservadas | pendente | não validado |
| Desktop/painel | painel inferior flutuante, centralizado, 56 px e com ícone Katu | pendente | não validado |
| Plasma | tema SVG Katu, esquema KatuDark derivado das artes | pendente | não validado |
| Dolphin/Settings/notificações | herdam o esquema do KDE e partes do Plasma Style | pendente | não validado |
| Calamares | seis pôsteres oficiais inteiros, proporção preservada | pendente | não validado |
| Welcome | arte oficial; no Live, escolha entre experimentar ou abrir `katu-installer`; arte redimensiona junto com a janela | pendente | não validado; alteração recente aguarda build |
| Plymouth | marca, spinner e pontos oficiais | pendente | não validado |
| Lockscreen | nenhuma mudança nesta etapa | pendente | não validado |
| GRUB | logo e seleção oficiais substituem os protótipos; entradas e parâmetros intactos | pendente | não validado |

## ISO CI da revisão `04fe5b6` (não aprovada)

- Estrutura estática da ISO: 11/11 verificações PASS (incluindo BIOS e UEFI).
- Smoke QEMU: FAIL por timeout total de 600 s antes do marcador de sessão Plasma/DBus/overlay. Os registros mostram `sddm.service` iniciado e `katu-live-autologin.service` finalizado, mas não confirmam que a sessão Plasma subiu.
- O teste soma o boot frio (~100 s até os serviços gráficos) ao polling de 550 s do serviço QA. Um timeout de 600 s podia matar QEMU antes da conclusão do diagnóstico. O limite global foi ampliado para 900 s e `TimeoutStartSec` do serviço QA para 780 s; a próxima build deverá confirmar o sucesso ou produzir diagnóstico completo.
- ISO SHA-256: `066b2e72a38a4777cfc57f28ad87913b6f1ee7658ff844fa645a75f92bccabfc`. Não testada em VirtualBox, instalada ou autenticada.

## Candidata local anterior (não é a revisão atual)

- ISO: `C:\\katuos\\dist\\KatuOS-Premium-1.0.1-rc1-d713b343-x86_64.iso` (SHA-256 `af6be41e5463538eefc7b59de9c7d35d650bfeb3e138a4084ff694d6fd382157`); anterior à revisão `04fe5b6`.
- Em UEFI, esta VM isolada não encontrou mídia inicializável; ao configurar BIOS e VBoxSVGA, o kernel iniciou e avançou por `networking.service` e `sound.target`, mas permaneceu no console sem desktop após cerca de dois minutos, com mensagens do driver VBoxVideo.
- Evidência: [candidate-premium-iso.png](FINAL-VISUAL-QA/candidate-premium-iso.png). Esta é uma falha/limitação observada dessa candidata e não foi promovida a PASS. O resultado da revisão atual será determinado pela ISO exata produzida no CI e testada novamente.
- O erro "Please insert a bootable medium" observado antes foi da configuração inicial da VM de QA sem controlador/mídia conectados; não usar essa primeira tela como resultado da ISO.

## Matriz de resolução e escala

`1024x768`, `1280x720`, `1366x768`, `1600x900`, `1920x1080`, `2560x1440` e escalas `100%`, `125%`, `150%`, `175%`, `200%`: **NOT AUTOMATICALLY VERIFIED**. A única captura disponível é da ISO anterior em 1024×768. Não marcar como aprovado até capturar a ISO nova em cada cenário possível.
