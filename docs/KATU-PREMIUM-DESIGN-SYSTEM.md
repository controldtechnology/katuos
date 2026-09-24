# Katu OS Premium Design System

## Princípios

Katu OS combina natureza brasileira, tecnologia acessível e identidade própria. A biblioteca oficial em `C:\katuos\imagens` é a origem de toda arte desta evolução. Não gerar novas ilustrações, logos ou wallpapers. Redimensionamentos e conversões só podem manter a composição original.

Ubuntu é referência de consistência, hierarquia, clareza e acabamento. Nenhum elemento de marca ou arte Ubuntu deve ser copiado.

## Paleta derivada dos assets

As cores abaixo foram amostradas diretamente dos wallpapers, slides e logos do pacote oficial:

| Token | Cor | Aplicação |
|---|---|---|
| `background` | `#041F16` | fundo Katu principal, amostra dominante do wallpaper Amazônia |
| `surface` | `#063723` | superfícies verdes dos logos e ilustrações |
| `surface-deep` | `#02140F` | painel, menu e superfícies elevadas escuras |
| `surface-raised` | `#10462B` | controles, cartões e superfícies selecionadas |
| `accent-green` | `#0F7B43` | ação e identidade em ícones/indicadores; evitar texto pequeno nesta cor sobre fundo escuro |
| `accent-amber` | `#E0B146` | foco, ação destacada, progresso e acentos |
| `text-primary` | `#F4F1E2` | texto principal off-white amostrado do logo oficial |
| `text-secondary` | `#C2CBBF` | texto secundário em SDDM/tema |
| `border-subtle` | `#326149` | contornos visíveis em controles escuros |

Os tokens claros estão definidos como direção visual, mas um esquema `KatuLight` instalável ainda não foi validado e permanece pendente. Mensagens de erro e aviso usam cores semânticas reconhecíveis e ícone/rótulo além da cor; não redefinem a paleta da marca.

## Contraste e acessibilidade

- Texto pequeno em superfícies escuras usa `text-primary` ou `text-secondary`, nunca `accent-green` como única indicação.
- Amber e verde identificam foco/seleção, mas todos os estados também têm forma, rótulo ou ícone.
- Foco de teclado deve ser contínuo e visível; controles desabilitados permanecem distinguíveis sem reduzir contraste de texto ativo.
- Testar escala 100%, 125%, 150%, 175% e 200%, além de 1024×768 a 2560×1440.
- Não embutir textos essenciais nos wallpapers: imagens oficiais com slogans/cartões ficam como opções editoriais e devem ser avaliadas por resolução.

## Tipografia e hierarquia

Usar Noto Sans quando já disponível no sistema. Não adicionar pacotes de fonte ou mudar listas funcionais nesta etapa. Títulos curtos e fortes; corpo em frases naturais de PT-BR; ajuda e legendas menores, mas sempre legíveis. Nomes de ações começam por verbos claros.

## Geometria e componentes

- Espaçamento em passos de 4 px; controles com alvo clicável mínimo aproximado de 40 px.
- Cantos discretos e consistentes, sem cartões excessivos ou blur pesado.
- Botão primário: superfície verde da marca ou âmbar com texto de contraste alto; foco âmbar. Secundário: superfície elevada e contorno sutil. Ghost: transparente com hover legível. Ação destrutiva deve usar rótulo explícito e cor semântica.
- Inputs: fundo profundo, borda visível, foco âmbar, erro com texto/ícone e descrição.
- Notificações e diálogos reutilizam superfícies e tipografia do Plasma; não imitar o mockup como se fosse um tema funcional.

## Uso de assets

- Logos finais: `imagens/katu-os-final-assets/branding/logo/`; escolher a variante conforme fundo e manter sua proporção.
- Slides de instalação: `imagens/katu-os-final-assets/installer/calamares/slides/`; usar os seis slides aprovados sem recompor a arte.
- Ícones de locais/dispositivos e aplicações: matrizes oficiais em `plasma/icons/` e `applications/`; gerar somente tamanhos de sistema a partir da matriz.
- Plymouth e GRUB têm matrizes dedicadas. Plymouth só pode trocar imagens no tema funcional existente. GRUB permanece intocado até a mudança visual poder ser testada com a ISO final.
- A prancha de cursor não é um tema XCursor instalável. Não ativar sem arquivos de cursor individuais.
- Imagens de mockup servem como referência visual, nunca como wallpaper, background de login ou screenshot de validação.

## Consistência por superfície

Plasma, menu, Dolphin, Configurações, notificações, SDDM, bloqueio e Calamares usam a mesma paleta, logos e escala tipográfica. Live e desktop instalado compartilham wallpaper, painel e menu padrão. SDDM usa uma fotografia/ilustração escura oficial sem formulário/texto embutido, com overlay contido que não apaga a arte.

## Limite de mudança

Arquivos visuais podem mudar quando a apresentação está isolada. Boot, kernel, initramfs, GRUB funcional, serviços, sessão Live, autenticação SDDM e módulos/configuração funcional do Calamares ficam protegidos. Se a integração exigir alterar esses mecanismos, manter o comportamento atual e registrar a pendência.
