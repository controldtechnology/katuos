# Arquivos alterados — evolução visual Katu OS

**Branch:** `visual/katu-premium-reconstruction`, derivada da baseline funcional. A tag original continua intacta.

## Visual/branding

- `sddm/katu/Main.qml`, `theme.conf`, `background.png`, `logo.png`: login responsivo e assets oficiais; autenticação/ações permanecem nas chamadas SDDM existentes.
- `plasma/look-and-feel/.../org.kde.plasma.desktop-layout.js` e espelho no include: painel inferior flutuante, centralizado e launcher Katu.
- `packages/katu-branding/usr/share/plasma/desktoptheme/katu/`: metadata e SVGs de superfície/seleção.
- `config/includes.chroot/usr/share/color-schemes/KatuDark.colors` e cópia no pacote: paleta derivada da biblioteca Katu.
- `packages/katu-branding/usr/share/wallpapers/katu/`: wallpaper desktop principal e alternativo limpos, além da coleção.
- `packages/katu-branding/usr/share/icons/Katu/` e hooks visuais: tema de ícones Katu que herda Breeze Dark, com símbolos oficiais para lugares e dispositivos.
- `packages/katu-welcome/usr/lib/katu-welcome/main.py` e `usr/share/katu/welcome/hero.png`: layout e hero visual; ações, processos, autostart e lógica de primeira execução preservados.
- `installer/calamares/branding/katu/show.qml`, branding e assets espelhados: composição editorial das lâminas oficiais; sequência técnica/modulos não tocados.
- `plymouth/katu/`: assets oficiais e apenas cores de fundo no script; animação e callbacks preservados.
- `grub/katu/` e espelhos em `config/includes.binary/boot/grub` e `config/includes.chroot/boot/grub`: logo e seleção aprovados substituem os protótipos antigos; nenhuma configuração ou entrada de boot mudou.
- Espelhos antigos em `config/includes.chroot/usr/share/`: wallpapers, logos, ícones e Plymouth foram sincronizados com os assets aprovados; ícones sem aplicação correspondente foram retirados.
- `docs/KATU-DESIGN-SYSTEM-2.md` e `output/FINAL-*.md`: direção de design e relatórios de inventário/QA.

## Funcional

**Nenhuma alteração intencional de lógica de boot, Live, autenticação ou instalação.** O arranjo do painel e os arquivos QML são visuais, porém ainda precisam de teste de runtime. Os relatórios separam testes estáticos de validação funcional da ISO.
