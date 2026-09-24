# Validação dos assets oficiais

**Estado:** em andamento; ainda não há nova ISO para auditoria visual final.

- Biblioteca `C:\katuos\imagens`: 76 arquivos, 74 PNG, 1 ZIP e 1 README.
- Grupo aprovado A: 35 PNGs do pacote final e 2 imagens limpas selecionadas na raiz (37 artes).
- Grupo bloqueado C: 37 PNGs antigos/promocionais/mockups. Os arquivos master foram preservados; o background legado do SDDM foi retirado da árvore que alimenta o build por estar obsoleto e ter texto composto.
- Auditoria por SHA-256 nas árvores de entrada `config`, `packages`, `installer`, `sddm`, `plymouth`, `grub` e `plasma`: **0 de 37 hashes do grupo C permanecem**. Antes da limpeza havia 23 hashes C distintos em artefatos de runtime; foram substituídos por assets aprovados ou removidos quando não havia aplicação correspondente.
- Assets A distintos incorporados nas árvores de runtime: **32 de 37**. Não significa validação visual: nenhum deles foi inspecionado dentro da nova ISO ainda.
- Arte nova gerada: nenhuma.

## Assets oficiais integrados na árvore de build

| Origem | Destino | Tela/componente | Evidência de arquivo |
|---|---|---|---|
| `ChatGPT Image 20 de set. de 2026, 17_12_03.png` | `packages/katu-branding/usr/share/wallpapers/katu/contents/images/katu-rio-4k.png` | Wallpaper desktop Live/instalado | cópia binária do asset da master |
| `ChatGPT Image 20 de set. de 2026, 17_11_00.png` | `sddm/katu/background.png`; `packages/katu-branding/usr/share/wallpapers/katu/contents/images/katu-amazonia-4k.png` | Login e wallpaper alternativo | cópia binária do asset da master |
| `branding/logo/katu-os-white.png` | `sddm/katu/logo.png`; `installer/calamares/branding/katu/logo.png` | SDDM e instalador | cópia binária |
| `branding/logo/katu-symbol-monochrome.png` | `installer/calamares/branding/katu/icon.png`; ícone hicolor `katu-logo.png` | Calamares e launcher | cópia binária |
| `installer/calamares/slides/slide-01.png` a `slide-06.png` | `installer/calamares/branding/katu/slide-*.png` | Slideshow | cópias binárias, slideshow usa `PreserveAspectFit` |
| `installer/live/katu-live-welcome.png` | `installer/calamares/branding/katu/welcome.png` | Welcome Calamares | cópia binária |
| `plasma/icons/katu-computer.png`, `katu-home.png`, `katu-network.png`, `katu-removable-drive.png`, `katu-trash-empty.png`, `katu-trash-full.png`, `katu-usb.png` | `packages/katu-branding/usr/share/icons/Katu/256x256/places/` | Computador, pasta, rede, mídia, lixeira e USB | cópias binárias com nome de função, registradas no tema Katu |
| `plymouth/katu/katu-logo-boot-light.png`, `spinner.png`, `progress-dot.png` | `plymouth/katu/` | Splash | cópias binárias; lógica de animação preservada |
| `branding/logo/katu-os-dark.png`, `katu-os-monochrome.png`, `katu-symbol-white.png` | `packages/katu-branding/usr/share/katu/branding/logos/` | Reserva de marca instalada | presentes no pacote; ainda sem tela que os exponha |

## Assets oficiais deliberadamente não usados

- Os dois PNGs curatoriais do GRUB são usados apenas como textura/logo; entradas, caminhos, geometria de tema e parâmetros de boot não foram alterados.
- `plasma/cursors/katu-cursor-master.png`: é uma prancha, não arquivos individuais XCursor; instalar a prancha não produziria cursores funcionais.
- Os wallpapers curatoriais `katu-rio-4k.png` e `katu-amazonia-4k.png` foram preservados na master, mas suas entradas de runtime usam imagens sem texto incorporado para não cobrir ícones, relógio e autenticação.
- Quatro ícones de aplicativos (`katu-backup`, `katu-feedback`, `katu-security`, `katu-system-info`) ficam fora de lançadores porque não há aplicativos correspondentes na lista de pacotes.

## Evidência visual

Há uma captura da ISO atualmente montada em `FINAL-VISUAL-QA/00-current-iso-1024x768.png`. Ela documenta o problema visual existente no login da ISO Golden Master; **não** valida os arquivos acima na nova ISO. A confirmação de que wallpapers, logos, ícones, Plymouth e slides realmente aparecem continua pendente de build e execução da ISO reconstruída.
