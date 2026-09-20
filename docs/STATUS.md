# STATUS — KATU OS

Atualizado: 2026-09-20

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
