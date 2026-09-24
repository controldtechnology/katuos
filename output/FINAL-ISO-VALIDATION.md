# Validação final da ISO Katu OS Premium

**Estado: EM ANDAMENTO — NÃO APROVADA PARA PRODUÇÃO.** Este relatório só poderá mudar para aprovado após testar a ISO exata da revisão atual numa VM limpa, incluindo Live, instalação, reboot, SDDM, login e desktop instalado.

| Campo | Resultado atual |
|---|---|
| Branch | `visual/katu-premium-reconstruction` |
| Baseline congelada | `katu-os-golden-master-functional` (`5ce81b589f5448deedb75b5317609f08c8e955d0`) |
| Revisão atual | `04fe5b6` |
| ISO desta revisão | Candidata gerada pelo GitHub Actions `36053210958`; não aprovada |
| Tamanho / SHA-256 | ISO: 3.467.735.040 bytes; SHA-256 `066b2e72a38a4777cfc57f28ad87913b6f1ee7658ff844fa645a75f92bccabfc` |
| Data de build | 2026-09-24 |
| Boot estrutural / GRUB / SquashFS / kernel / initrd / Live / Calamares / branding / UEFI / BIOS | PASS na validação estática da ISO |
| Smoke Live em QEMU (SDDM/Plasma/overlay) | FAIL: timeout total de 600 s venceu antes de o serviço QA completar sua espera/diagnóstico de Plasma |
| SDDM iniciado / autologin service | PASS nos registros seriais; serviço de diagnóstico iniciou; presença da sessão Plasma permanece NÃO CONFIRMADA |
| Instalação / boot pós-instalação | NOT RUN |
| Calamares / instalação / boot pós-instalação | NOT RUN |
| SDDM, login e desktop instalado | NOT RUN |
| Resoluções / escalas | NOT AUTOMATICALLY VERIFIED |
| Problemas confirmados na baseline | SDDM sem campos de senha/entrada em captura 1024×768 |
| Problema na candidata local d713 | BIOS iniciou serviços mas não mostrou desktop; ver evidência visual |
| Pendências | corrigir timeout do smoke, rebuildar, confirmar Plasma/overlay, testar VM da ISO exata, instalação limpa, screenshots |

Não declarar a ISO pronta, íntegra para produção ou 100% saudável antes de concluir todos os testes pendentes.
