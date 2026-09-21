# Katu OS — Guia de Instalação

## Requisitos Mínimos

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 64-bit dual-core 1 GHz | Quad-core 2+ GHz |
| RAM | 2 GB | 4 GB+ |
| Armazenamento | 20 GB | 40 GB+ (SSD recomendado) |
| Gráficos | OpenGL 2.0 | OpenGL 3.3+ |
| Firmware | BIOS ou UEFI | UEFI com Secure Boot |

## Criar Pendrive Bootável

Consulte `docs/CRIAR-PENDRIVE.md` para instruções detalhadas.

**Resumo rápido:**

```bash
# Linux (substitua /dev/sdX pelo seu pendrive — CUIDADO)
sudo dd if=katu-os-1.0-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

No Windows: use **balenaEtcher** (gratuito) ou Rufus.

## Processo de Instalação

### 1. Boot pelo Pendrive

1. Reinicie o computador
2. Pressione a tecla de boot (`F12`, `F8`, `Del` — varia por fabricante)
3. Selecione o pendrive Katu OS
4. Na tela GRUB, escolha **"Experimentar Katu OS"**

### 2. Sessão Live

O sistema inicia sem instalar nada. Você pode:
- Testar o hardware (Wi-Fi, som, gráficos)
- Navegar na internet com Firefox
- Usar o Calamares para instalar

### 3. Iniciar Instalação

Na área de trabalho, clique em **"Instalar Katu OS"** ou abra pelo menu Katu Welcome.

### 4. Etapas do Calamares

| Etapa | O que configurar |
|-------|-----------------|
| **Bem-vindo** | Verificações de sistema |
| **Localização** | Região: América / Fuso: São Paulo |
| **Teclado** | Layout: Brasil (ABNT2) |
| **Particionamento** | Automático (recomendado) ou manual |
| **Usuário** | Nome, login, senha do computador |
| **Resumo** | Revisar antes de instalar |
| **Instalação** | ~10–20 minutos dependendo do disco |
| **Conclusão** | Reiniciar |

### 5. Particionamento

#### Automático (recomendado para iniciantes)
- Usa o disco inteiro
- Cria partição EFI (300 MB), raiz ext4, swapfile automático
- **Apaga todos os dados do disco**

#### Manual
- Para dual-boot com Windows: não apague a partição EFI do Windows
- Crie partição `/` ext4 (mínimo 15 GB)
- Particiona `/home` separada é opcional mas recomendada

### Dual Boot com Windows

1. No Windows, abra **Gerenciamento de Disco** e libere espaço (20+ GB)
2. No Calamares, escolha **"Instalar ao lado do Windows"**
3. O GRUB detecta o Windows automaticamente via `os-prober`

## Pós-instalação

Após reiniciar no sistema instalado:

1. **Katu Welcome** abre automaticamente no primeiro login
2. Execute **"Atualizar sistema"** para garantir que tudo está atualizado
3. Se precisar de codecs extras, use o gerenciador de pacotes

## Verificar Integridade da ISO

```bash
sha256sum -c katu-os-1.0-amd64.iso.sha256
```

O arquivo `.sha256` está disponível junto com a ISO.

## Suporte

- GitHub Issues: https://github.com/katuos/katu-os/issues
- Documentação completa: `docs/`
