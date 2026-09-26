# Katu OS — ISO Baseline

> Registrado em: 2026-09-25  
> Branch: `visual/katu-brand-identity`  
> Propósito: preservar referência da ISO estável antes do rebranding visual definitivo v2

---

## ISO Principal (dist/)

| Campo | Valor |
|-------|-------|
| **Nome** | `KatuOS-Premium-1.0.1-rc1-66973a00-x86_64.iso` |
| **Caminho** | `C:\katuos\dist\KatuOS-Premium-1.0.1-rc1-66973a00-x86_64.iso` |
| **Tamanho** | 3,467,739,136 bytes (3.23 GB) |
| **SHA256** | `a86d37563af171dc83a0bebdcd6653714f71fc432e3e497186a760ffd9bded2d` |
| **Data** | 2026-09-25 13:33 |
| **Status** | ESTÁVEL — NÃO SOBRESCREVER |

## ISO Candidata (output/)

| Campo | Valor |
|-------|-------|
| **Nome** | `katu-os-1.0.1-rc1-amd64.iso` |
| **Caminho** | `C:\katuos\output\manual-review-35980066932\candidate-20260924T091825Z-5ce81b58\katu-os-1.0.1-rc1-amd64.iso` |
| **Tamanho** | 3,514,912,768 bytes (3.27 GB) |
| **SHA256** | `6d992b91b5978a4cd61d8bf82942405f577ca0501409c784755c46fccfea6dfd` |
| **Data** | 2026-09-24 07:22 |
| **Status** | Candidata anterior — preservar para comparação |

---

## Git Checkpoint

| Campo | Valor |
|-------|-------|
| **Branch** | `visual/katu-brand-identity` |
| **Commit HEAD** | `d713b34` — Apply official Katu visual assets and themes |
| **Tag criada** | `baseline/pre-rebranding-visual-v2-20260925` |

---

## Nova ISO (a ser gerada)

| Campo | Valor |
|-------|-------|
| **Nome** | `katu-os-1.0-visual-v2-amd64.iso` |
| **Destino** | `output/` |
| **Status** | A gerar após validação completa dos assets |

---

## Regra

A ISO em `dist/` e em `output/manual-review*/` **não devem ser sobrescritas**.  
A nova ISO terá nome diferente e será gerada em `output/` com novo timestamp.
