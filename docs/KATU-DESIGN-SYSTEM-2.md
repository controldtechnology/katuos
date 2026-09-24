# Katu OS Design System 2.0

**Estado:** direção visual aprovada para implementação, ainda não validada no Plasma.
**Base:** assets inspecionados em `C:\katuos\imagens`, especialmente o pacote final Katu, o wallpaper Rio/Jaguar e o fundo botânico do SDDM.
**Benchmark:** princípios de hierarquia, clareza e previsibilidade de um desktop maduro; marca, arte e linguagem seguem próprias do Katu OS.

## Direção de produto

**Brasil contemporâneo, natureza viva, tecnologia para todos.** A interface traduz mata profunda, água de rio e luz âmbar ao entardecer. O desktop prioriza leitura e familiaridade; as artes de onça e paisagem ficam concentradas em pontos editoriais, sem estampar cada controle.

A assinatura visual será a **linha do rio**: um traço âmbar fino que acompanha seleção e progresso ativo, curvado apenas em transições específicas do launcher. Ela aparece em poucos lugares e não substitui indicadores, ícones ou texto.

## Auditoria cromática

A amostragem quantizada das 35 artes do pacote final encontrou maior presença nos tons `#002211`, `#001111`, `#003322`, `#114433`, `#DDAA44` e `#EEEEDD`. O tema usa essa distribuição: superfícies floresta como base, creme para texto e âmbar reservado a foco/estado ativo. O verde luminoso é acento pontual, não preenchimento universal.

| Token | Cor | Uso |
|---|---|---|
| `forest-950` | `#001111` | Fundo recuado e scrim |
| `forest-900` | `#002211` | Fundo principal |
| `forest-800` | `#003322` | Superfície e menu |
| `forest-700` | `#114433` | Superfície elevada, borda subtil |
| `leaf-600` | `#117744` | Ação secundária e seleção discreta |
| `leaf-400` | `#33CC77` | Foco/estado positivo, uso contido |
| `sun-500` | `#DDAA44` | Linha ativa e realce editorial |
| `sun-400` | `#FFCC55` | Alerta e foco de alto contraste |
| `paper-100` | `#EEEEDD` | Texto primário e ícone claro |
| `paper-300` | `#C8D3C9` | Texto secundário |
| `paper-500` | `#9CAB9F` | Texto auxiliar, nunca para conteúdo essencial de baixo contraste |
| `error-500` | `#C85C55` | Erro, com ícone e descrição |
| `info-400` | `#75B9C6` | Informação, com ícone e rótulo |

A implementação deverá medir contraste nos pares finais antes de publicar o esquema. Os nomes seguem tokens semânticos; componentes não devem inserir hexes próprios.

## Tipografia

- **Noto Sans** para interface, corpo, menus e controles, desde que confirmada no manifesto de pacotes da base.
- Escala em `px` lógica: 12 legenda; 13 auxiliar; 14 corpo; 16 corpo destacado; 20 título de painel; 28 título de tela; 36 display editorial.
- Pesos: 400 corpo, 500 rótulos, 600 ação/título curto, 700 somente chamadas de boas-vindas.
- Texto de botão e ação em sentence case; frases curtas em PT-BR.
- O wordmark Katu é imagem oficial, não fonte de interface.

## Geometria e profundidade

- Grid base de 4 px. Espaços válidos: `4, 8, 12, 16, 24, 32, 48, 64`.
- Raio: `6 px` controles compactos; `10 px` cards; `16 px` launcher e dialogs.
- Borda: `1 px` em `forest-700`; `2 px` de foco em âmbar ou creme.
- Elevação: uma sombra macia curta em menus; duas camadas em modal. Sem glow e sem blur forte.
- Motion: 120 ms hover/foco e até 180 ms abertura de popup; transições podem ser desligadas pelo usuário e não são necessárias para compreender estado.
- Alvos clicáveis de ao menos 40×40 px, preferencialmente 44×44 px.

## Componentes

| Componente | Default | Interação | Acessibilidade |
|---|---|---|---|
| Primário | creme sobre folha escura | âmbar no foco; contraste invertido em pressed | foco visível, rótulo verbal |
| Secundário | fundo `forest-800` e borda | superfície `forest-700` | não depende apenas da cor |
| Ghost | transparente | fundo discreto ao hover | foco com contorno de 2 px |
| Destrutivo | vermelho `error-500` com texto | nunca usar vermelho para ação neutra | ícone + confirmação contextual |
| Campo | `forest-950`, texto creme | borda âmbar no foco; mensagem abaixo | placeholder nunca substitui label |
| Card | `forest-800`, borda subtil | sombra/realce somente se acionável | área de ação completa e foco |
| Notificação | `forest-800`, título e frase | ação única clara, fechamento identificável | cor + ícone + texto |
| Progresso | trilho `forest-700`, avanço verde/âmbar | animação suave | percentual e etapa em texto |
| Menu contextual | superfície opaca | seleção de alto contraste | navegação por teclado e setas |

## Shell: desktop e painel inferior

Wireframe escolhido:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  Katu River/Jaguar                         janela / arquivos / widgets  │
│  sujeito à safe area                      céu e rio preservados         │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│ [Katu] [fixados] [tarefas abertas........] [rede áudio energia 24/09]  │
└────────────────────────────────────────────────────────────────────────┘
```

O painel permanece no rodapé e conserva semântica KDE (tarefas, bandeja, relógio), mas recebe novo ritmo: altura alvo de 56 px, padding horizontal de 12 px, grupos com 8/16 px de separação, linha superior discreta e marcador âmbar sob a tarefa ativa. Em 1024×768, reduzir paddings antes de ocultar comandos; bandeja e relógio continuam disponíveis.

O launcher abre para cima, com largura preferencial de 720 px, altura até 600 px e limites definidos pelo espaço de tela. Busca fica no topo; categorias em uma rail lateral estreita; favoritos e aplicativos ocupam o conteúdo; usuário e energia ficam no rodapé. A estrutura precisa colapsar para uma coluna quando a tela tiver menos de 650 px de largura útil. Resultado selecionado mostra nome e categoria, nunca somente o ícone.

**Risco técnico conhecido:** modelos de aplicativo do launcher Kickoff vivem no plugin QML `org.kde.plasma.private.kicker`. Um plasmoid próprio só o usará se o import e as classes forem verificados contra Plasma 6.3.6 da ISO. Caso contrário, o fallback visual será uma configuração refinada do launcher upstream, preservando o modelo oficial de aplicativos.

## Wallpapers e safe area

- Wallpaper padrão planejado: `ChatGPT Image 20 de set. de 2026, 17_12_03.png`, paisagem sem lettering, jaguar à esquerda e rio com espaço negativo à direita.
- Fundo do SDDM: `17_11_00.png`, mata abstrata sem texto; manter a arte perceptível e reservar o centro escuro para autenticação.
- Coleção oficial 4K permanece no seletor com identificação e preview. Como as seis artes incluem wordmark/texto dentro da imagem, não colocar ícones nem widgets sobre essas áreas e inspecionar recortes em todas as proporções.
- Nenhum texto de interface será embutido na imagem por geração. Redimensionamento/crop técnico usa o PNG oficial sem alteração artística.
- Testar 1024×768, 1280×720, 1366×768, 1600×900, 1920×1080 e 2560×1440. Em 4:3 usar alinhamento que preserve a onça sem cortar; verificar manualmente antes de aceitar.

## SDDM e lockscreen

SDDM terá composição em duas zonas sem dimensões absolutas: arte de fundo integral e painel de autenticação compacto ancorado ao espaço negativo, com logo branco oficial, usuário, campo de senha, botão, sessão e energia. Hora/data são secundárias. A raiz usa dimensões reais do `Screen`; painel respeita margens mínimas de 24 px e altura de viewport. Mensagens de autenticação não podem deslocar os controles para fora da tela.

Lockscreen compartilha cores e arte, mas concentra a hora/data e mantém somente a ação de desbloqueio. A autenticação, `authenticator`, callbacks e chamadas SDDM existentes permanecem intactos. Não será introduzido novo fluxo de usuário/senha.

## Calamares

O instalador conserva módulo, ordem, particionamento e lógica existente. A integração Katu usa logo oficial, seis slides e Welcome oficiais; melhora contraste, padding, título de etapa, progresso e hierarquia de ação com QSS/QML de branding. Não replicar texto embutido nas artes. Se uma mudança visual exigir editar a sequência técnica, ela é cancelada.

## Ícones e aplicações

- Ícones de lugares e dispositivos oficiais são aplicados por função, em tamanhos rasterizados a partir da master e conferidos a 16/22/32/48/64 px.
- Ícone de aplicação só será associado a aplicativo que exista na lista de pacotes; os quatro ícones de apps sem pacote ficam fora do menu.
- A prancha de cursores só vira tema XCursor depois de ser convertida em cursores individuais e validada. Não instalar a prancha como cursor.
- Favoritos padrão: Dolphin, navegador existente, configurações, instalador no Live; não criar lançadores para apps inexistentes.

## Acessibilidade

- Validar contraste WCAG 2.2 AA para texto normal e controles antes de fechar a paleta.
- Confirmar foco de teclado, operação sem mouse, rótulo sempre visível e mensagens de erro ligadas ao campo.
- Escala 100%, 125%, 150%, 175%, 200%; remover dimensões fixas em QML, permitir wrap e aumentar scroll em vez de cortar.
- Estado é comunicado por texto/ícone/forma além da cor; sistema reduz movimento quando a preferência está ativa.

## Critério de implementação

O painel/launcher precisa demonstrar mudança de layout e comportamento em screenshot, não só mudança de cor. Antes de cada tema/arquitetura nova: testar em Plasma 6.3.6, gerar screenshot, comparar, corrigir e só então sincronizar no include chroot. GRUB, boot, Live, SDDM autenticação e Calamares técnico são áreas protegidas. Build ISO final aguarda QA visual e funcional completos.
