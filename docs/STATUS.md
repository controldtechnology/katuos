# STATUS — KATU OS

Atualizado: 2026-09-22

## Situação atual — build concluído e boot live aprovado no VirtualBox

- Build [35756634827](https://github.com/controldtechnology/katuos/actions/runs/35756634827): concluído com sucesso em 24m53s.
- Commit: `ed2dab67f83493bc63ff8286805d5035df457f0b`.
- Validação de conteúdo da ISO (kernel, initrd, squashfs e GRUB): aprovada no CI.
- Artefato: `katu-os-1.0-amd64-iso`, disponível no build acima.
- Cópia local: `output/build-35756634827/katu-os-1.0-amd64.iso` (3.499.745.280 bytes); download concluído e SHA-256 conferido com o arquivo publicado em 2026-09-22.
- SHA-256: `bd8ad41d1cbd43104e04adedc6890c1ea5ab8b63fd9311ab35ee66939f47bc1f`.
- A etapa de criar Release GitHub foi pulada; este build disponibilizou um artefato do Actions.
- Correções de boot presentes no código: remoção de `splash`, blacklist de `vmwgfx`, `live-media=removable` e reforços no live-boot/initramfs.
- Teste em 2026-09-22: ISO iniciou até o KDE Plasma, com wallpaper Katu e centro de boas-vindas visíveis, sem BusyBox.
- VM: `Katu-ISO-35756634827`; VirtualBox 7.2.18; 3072 MB RAM; 1 CPU; EFI; VBoxSVGA; 128 MB VRAM; 3D desligado; ISO em DVD SATA; sem disco de instalação.
- Evidência: `output/virtualbox/boot-test.png`.
- Primeira tentativa com 2 CPUs não avançou do firmware EFI durante a observação. Ao reiniciar com 1 CPU, o boot chegou ao Plasma. O log do host registrou execução NEM/Hyper-V em modo lento; a causa exata da parada com 2 CPUs não foi determinada.
- Mensagens de erro de `vboxvideo` apareceram durante o boot, mas não impediram a sessão gráfica.
- Escopo validado: inicialização live até o desktop. Instalação em disco e funcionamento dos aplicativos ainda não foram testados.

### Falha encontrada no primeiro teste de instalação

- O particionamento e a cópia do sistema concluíram no VDI de 40 GiB.
- A instalação parou no bootloader com `grub-install ... returned error code 127`.
- Causa: o módulo `packages` removia o Calamares e executava a limpeza de dependências antes do módulo `bootloader`; o conjunto GRUB podia ser marcado como automático e removido.
- Correção aplicada: GRUB/EFI agora é marcado como manual no hook final e explicitamente preservado pelo módulo `packages` antes da etapa de bootloader. A validação do build também exige esse conjunto.
- Build corrigido concluído: [35853181664](https://github.com/controldtechnology/katuos/actions/runs/35853181664), commit `a095e62`.
- As validações do instalador no sistema construído e da ISO passaram; artefato `katu-os-1.0-amd64-iso` (ID `10747151747`) disponível no build.
- Teste manual no VDI: depois de preservar o GRUB, `grub-install` terminou sem erros e `grub-mkconfig` encontrou kernel e initrd. O primeiro boot automático pelo VDI ainda não foi capturado porque a sessão do VirtualBox perdeu o registro durante o desligamento.

O registro abaixo é histórico (2026-09-20); as indicações de build não executado e bloqueio por ambiente Linux foram superadas pelo build no GitHub Actions.

## Registro histórico

---

## FASE ATUAL: INFRAESTRUTURA (FASE 1)

---

## IMPLEMENTADO

| Item | Descrição |
|------|-----------|
| Estrutura de diretórios | Completa |
| docs/AUDITORIA-INICIAL.md | Auditoria do ambiente |
| docs/ARCHITECTURE.md | Arquitetura do projeto |
| docs/STATUS.md | Este arquivo |
| VERSION | 1.0-alpha |
| .gitignore | Configurado |
| config/live-build.conf | Parâmetros do build |
| config/package-lists/ | Listas de pacotes |
| config/hooks/ | Hooks de build |
| config/bootloaders/ | GRUB config |
| packages/katu-branding/ | Estrutura do pacote |
| packages/katu-default-settings/ | Estrutura do pacote |
| packages/katu-welcome/ | Estrutura + app Python |
| packages/katu-release/ | /etc/os-release |
| plasma/ | Configuração KDE completa |
| sddm/ | Tema SDDM |
| plymouth/ | Tema Plymouth |
| grub/ | Tema GRUB |
| installer/calamares/ | Configuração Calamares |
| scripts/setup-build-env.sh | Setup do ambiente Linux |
| scripts/build.sh | Script de build principal |
| scripts/clean.sh | Limpeza de artefatos |
| scripts/validate.sh | Validação do projeto |
| scripts/checksum.sh | Geração de checksums |
| README.md | Documentação principal |

---

## TESTADO

| Item | Status |
|------|--------|
| Nenhum item testado ainda | — |

*Build ainda não executado — aguardando ambiente Linux*

---

## FUNCIONANDO

| Item | Status |
|------|--------|
| Nenhum item verificado | — |

---

## FALHANDO

| Item | Problema |
|------|----------|
| Nenhuma falha registrada | — |

---

## BLOQUEADO

| Item | Bloqueio |
|------|----------|
| BUILD-001 | Virtualização desabilitada no BIOS — WSL2/Docker não disponíveis |

---

## PENDENTE

| Item | Prioridade |
|------|-----------|
| Assets visuais (logos, wallpapers) | ALTA |
| Habilitar virtualização no BIOS | CRÍTICA |
| Instalar WSL2 | CRÍTICA |
| Executar BUILD-001 | CRÍTICA |
| Testar boot da ISO | ALTA |
| Integrar KDE Plasma personalizado | ALTA |
| Integrar Calamares | ALTA |
| Criar Katu Welcome | MÉDIA |

---

## PRÓXIMA ETAPA

**Ação necessária do usuário:**

1. Reiniciar o computador
2. Entrar no BIOS/UEFI
3. Habilitar "Intel VT-x" / "Intel Virtualization Technology"
4. Salvar e reiniciar
5. Executar: `wsl --install`
6. Reiniciar
7. Executar: `wsl --install -d Debian`
8. No WSL2 Debian:
   ```bash
   cp -r /mnt/c/katuos ~/katuos
   cd ~/katuos
   bash scripts/setup-build-env.sh
   bash scripts/build.sh
   ```

---

## ROADMAP DE BUILDS

```
[ ] BUILD-001 — ISO mínima Debian Live
[ ] BUILD-002 — KDE Plasma
[ ] BUILD-003 — Branding Katu
[ ] BUILD-004 — Calamares
[ ] BUILD-005 — Apps + Drivers
[ ] BUILD-006 — Katu Welcome
[ ] BUILD-007 — QA
[ ] RC-001    — Release Candidate
[ ] 1.0       — Release Final
```

---

*Atualizar após cada fase concluída*
