# Katu OS — Decisões de Sistema de Arquivos

## Escolha: ext4

O Katu OS 1.0 usa **ext4** como sistema de arquivos padrão para a partição raiz.

### Justificativa

| Critério | ext4 | Btrfs |
|----------|------|-------|
| Estabilidade em Debian | Produção desde 2008 | Estável mas mais complexo |
| Suporte a ferramentas | Universal | Requer btrfs-progs |
| Recuperação de falhas | Madura | Mais moderna (checksums) |
| Curva de aprendizado | Baixa | Média/Alta |
| Compatibilidade com Calamares | Nativa | Requer configuração extra |
| Desfragmentação para SSD | `discard` | `autodefrag` |

Para a versão 1.0 (público geral, primeiro contato com Linux), **ext4 é a escolha correta**: sem surpresas, amplamente documentada, e todo suporte da comunidade Debian cobre ext4 por padrão.

### Configuração padrão do Calamares

```
defaultFileSystemType: ext4
efiSystemPartitionSize: 300M
```

Opções de montagem aplicadas automaticamente:
- HDD: `defaults`
- SSD: `defaults,discard`

### Swap

O Calamares cria um **swapfile** em vez de partição de swap dedicada, via `fstab.conf`. Isso é mais flexível (pode ser redimensionado sem reparticionamento).

### Btrfs no futuro

Katu OS 1.1 ou 2.0 poderá oferecer Btrfs como opção avançada no instalador, com subvolumes `@` (raiz) e `@home` para suporte a snapshots via Snapper.

### Particionamento Guiado

| Modo | Partições Criadas |
|------|-------------------|
| BIOS/MBR | `/boot` ext4 512MB, `/` ext4, swap file |
| UEFI/GPT | `/boot/efi` FAT32 300MB, `/` ext4, swap file |
