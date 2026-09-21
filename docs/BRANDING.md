# Katu OS — Identidade Visual e Branding

## Valores da Marca

O Katu OS representa a biodiversidade, inovação e cultura brasileira.

- **Katu** — palavra de origem Tupi, significa "bom/correto"
- **Missão**: Linux acessível, bonito e funcional para o Brasil
- **Personalidade**: Moderno, acolhedor, verde amazônico

## Paleta de Cores

| Nome | Hex | Uso |
|------|-----|-----|
| Katu Escuro | `#1a1a1a` | Background principal |
| Katu Esmeralda | `#2ecc71` | Accent principal (seleção, foco, botões) |
| Katu Ouro | `#f39c12` | Accent secundário (destaques, avisos) |
| Katu Claro | `#ecf0f1` | Texto em fundo escuro |
| Katu Verde Escuro | `#102018` | Background Plymouth |

## Tipografia

- **Interface**: Noto Sans 10pt (variável: Regular, Bold)
- **Monospace**: Noto Mono 10pt (terminal, código)
- **Emoji**: Noto Color Emoji

Noto foi escolhido pela cobertura Unicode completa, incluindo caracteres especiais do português e suporte a todos os idiomas do Brasil indígena.

## Logo

O logo do Katu OS consiste em:
- Símbolo: folha/ave estilizada em verde esmeralda
- Tipografia: "katu OS" em Noto Sans Bold, lowercase
- Versão escura: texto branco, símbolo esmeralda
- Versão clara: texto preto, símbolo esmeralda

### Variantes disponíveis

| Arquivo | Dimensão | Uso |
|---------|----------|-----|
| `katu-logo-final.png` | 1024×1024 | Master, ícones grandes |
| `katu-logo-light.png` | 1024×1024 | Fundos escuros |
| `katu-logo-dark.png` | 1024×1024 | Fundos claros |
| `katu-logo-boot-light.png` | 400×150 | Plymouth (barra de boot) |
| `katu-grub-logo.png` | 200×100 | Menu GRUB |

## Temas

### KatuDark (padrão)
- Background: `#1a1a1a`
- Accent: `#2ecc71` (esmeralda)
- Arquivo: `plasma/colors/KatuDark.colors`

### KatuLight
- Background: `#ffffff` / `#f0f0f0`
- Accent: `#2ecc71` (esmeralda — mesma)
- Arquivo: `plasma/colors/KatuLight.colors`

O usuário pode alternar entre os temas via **Configurações do Sistema → Esquema de Cores**.

## Wallpapers

6 wallpapers 4K disponíveis, todos com tema amazônico/brasileiro:

| Arquivo | Tema |
|---------|------|
| `katu-amazonia-4k.png` | Floresta Amazônica — padrão |
| `katu-cerrado-4k.png` | Cerrado brasileiro |
| `katu-pantanal-4k.png` | Pantanal |
| `katu-caatinga-4k.png` | Caatinga |
| `katu-mata-atlantica-4k.png` | Mata Atlântica |
| `katu-campos-4k.png` | Campos do Sul |

## Aplicação nos Componentes

| Componente | Arquivo de tema |
|------------|----------------|
| KDE Plasma colors | `KatuDark.colors` / `KatuLight.colors` |
| SDDM login | `sddm/katu/Main.qml` |
| Plymouth boot | `plymouth/katu/katu.script` |
| GRUB | `grub/katu/theme.txt` |
| Calamares | `installer/calamares/branding/katu/` |
| Ícones | `plasma/icons/katu/` + hicolor |
| Look & Feel | `plasma/look-and-feel/org.katuos.desktop/` |

## Diretrizes de Uso

- O nome "Katu OS" é marca registrada do projeto
- Derivativos devem remover logos e referências à marca Katu OS
- Código é licenciado MIT; assets visuais têm copyright reservado
- Consulte `docs/LICENSES.md` para detalhes completos
