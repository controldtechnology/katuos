# Validação da ISO candidata Katu OS Premium

**Estado: candidata funcionalmente testada em parte; não aprovada para produção.** Não há garantia de compatibilidade universal nem aprovação visual final.

Os resultados abaixo descrevem somente a ISO já testada do commit `48223e8`. Há correções visuais no SDDM/Calamares e uma checagem Qt 6 em andamento no worktree; elas ainda precisam de build e teste na próxima ISO.

| Campo | Resultado |
|---|---|
| Revisão | `48223e8` — `Avoid duplicate welcome in Live session` |
| CI | [run 36129854861](https://github.com/controldtechnology/katuos/actions/runs/36129854861) |
| Artifact | [baixar ISO candidata](https://github.com/controldtechnology/katuos/actions/runs/36129854861/artifacts/10862656663) |
| Arquivo local | `C:\katuos\dist\manual-review-36129854861\candidate-20260925T113429Z-48223e86\katu-os-1.0.1-rc1-amd64.iso` |
| Tamanho | 3.468.062.720 bytes |
| SHA-256 | `f6f0fddb170e63c0c0555d0f5979946c1cf14f16c08fccc657f08ef587aa32ca` |
| Build/estrutura/QEMU Live smoke | PASS; 11 verificações estruturais e smoke automatizado passaram. |
| VirtualBox Live | PASS em BIOS/Legacy, VBoxSVGA, 1024×768. |
| Calamares/instalação | PASS em disco vazio de QA de 32 GiB, BIOS/MBR. Conclusão do instalador observada. |
| Boot pós-instalação sem ISO | PASS em BIOS/MBR. |
| SDDM/login/desktop | PASS funcional em BIOS/MBR; tela SDDM visualmente clara/genérica. |
| UEFI manual | NOT TESTED. |
| Outras resoluções/escalas | NOT TESTED. |

## Pendências visuais e de cobertura

SDDM e conteúdo principal do Calamares ainda não atingem a integração visual premium pretendida. Lockscreen, Dolphin, configurações, notificações, calendário e matriz de resoluções/escalas não foram aprovados. Portanto esta candidata serve para revisão e teste, não como release de produção.

## Baseline

A baseline funcional tagueada `katu-os-golden-master-functional` em `5ce81b589f5448deedb75b5317609f08c8e955d0` foi mantida separada. O arquivo ISO de baseline não foi substituído.
