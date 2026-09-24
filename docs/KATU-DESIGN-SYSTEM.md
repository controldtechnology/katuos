# Katu OS Design System

**Direção:** Brasil contemporâneo, natureza viva, tecnologia para todos.  
**Princípios:** reconhecimento sem excesso de ornamento; leitura antes do efeito; mesmas regras no login, desktop e instalador; base técnica preservada.

## Propósito da marca

O Katu OS é um sistema brasileiro, livre e acessível a quem está começando. A interface deve transmitir segurança e clareza. Amazônia, rios, mata, luz e onça-pintada são referências de origem e autoria, usadas como arte editorial ou assinatura gráfica — não como textura repetida atrás de cada componente.

## Cores e tokens

O registro legível por máquina está em `branding/tokens/katu-tokens.json`; esta tabela explica o uso de cada token.

| Token | Valor | Uso |
|---|---|---|
| `background-primary` | `#0d1117` | Plano principal escuro |
| `surface-primary` | `#161b22` | Janelas, menus e campos |
| `surface-elevated` | `#1c2128` | Popovers e superfícies elevadas |
| `border-default` | `#30363d` | Separação de controles e cartões |
| `border-subtle` | `#21262d` | Divisores de baixo contraste |
| `border-focus` | `#00c853` | Foco de teclado e controle ativo |
| `text-primary` | `#e6edf3` | Texto principal escuro |
| `text-secondary` | `#b1bac4` | Texto de apoio legível |
| `text-muted` | `#8b949e` | Metadados, nunca instrução essencial |
| `text-inverse` | `#0d1117` | Texto em botão verde claro |
| `accent-primary` | `#00c853` | Ação principal, foco e progresso |
| `accent-hover` | `#00e676` | Hover de ação |
| `accent-active` | `#00a040` | Pressionado |
| `status-success` | `#3fb950` | Sucesso |
| `status-warning` | `#ffab00` | Atenção e avisos |
| `status-error` | `#f85149` | Erro |
| `status-info` | `#58a6ff` | Informação e links |

O âmbar é reservado a avisos e acentos pequenos. O verde não deve ser a única indicação de estado; combinar cor com ícone, texto, contorno ou forma. Para o tema claro, manter os mesmos acentos e estados, com superfícies e texto ajustados para contraste. Não usar texto cinza apagado para instruções importantes.

Esses tokens são a referência de design. Cada formato de KDE/Qt pode exigir sintaxe própria; alterações em arquivos que geram a imagem devem ser classificadas como visuais antes da edição. Não introduzir script de geração que altere o build nesta fase.

## Tipografia

- **Família de interface:** Noto Sans, com fallback do sistema.
- **Monoespaçada:** Noto Mono apenas para código e dados alinhados.
- **Títulos:** peso semibold/bold, tamanho moderado e frase em caixa de sentença.
- **Corpo:** regular, espaçamento confortável e PT-BR natural.
- **Controles e menus:** rótulos curtos, pelo menos 12–14 px em densidade usual; respeitar a escala do sistema.
- Não usar tipografia decorativa em autenticação, navegação, estado ou instrução.

## Geometria e componentes

- Espaçamento derivado de uma grade de 4 px: 4, 8, 12, 16, 24 e 32 px.
- Cantos pequenos para controles e médios para cartões; evitar arredondamento excessivo.
- Bordas discretas; sombra apenas para separar camadas, sem blur pesado.
- **Botão principal:** verde Katu, texto escuro e foco externo claro.
- **Secundário:** superfície elevada e borda visível.
- **Ghost:** transparente até hover/foco, sem desaparecer em fundo escuro.
- **Perigoso:** rótulo explícito e vermelho reservado a ação destrutiva.
- **Campo:** fundo de superfície, placeholder secundário, borda e foco nítidos.
- **Erro:** mensagem junto do controle afetado, em texto e cor; manter a hierarquia e o foco.
- **Notificação:** título, mensagem e ação claramente separados; informação não depende somente da cor.

## Safe area e responsividade

- Deixar ao menos 24 px de respiro nas telas pequenas e 4% da largura em fundos de apresentação.
- Nunca embutir slogan, logo ou controle essencial no wallpaper do desktop.
- Usar dimensões reais da tela, limites mínimos/máximos e quebra de layout; evitar canvas fixo em 1920 × 1080.
- Testar 1024 × 768, 1280 × 720, 1366 × 768, 1600 × 900, 1920 × 1080 e 2560 × 1440. Validar proporções 4:3, 16:10 e 16:9.
- Testar escala em 100%, 125%, 150%, 175% e 200%; em resoluções/densidades indisponíveis, marcar como não verificada.

## Wallpapers e linguagem gráfica

- Wallpapers de trabalho: sem palavras, logotipos ou informação junto às bordas; contraste calmo e áreas com pouca informação atrás de ícones e janelas.
- Direções: `Katu Jaguar` (onça como arte editorial), `Katu Amazon` (mata contemporânea), `Katu River` (curso de rio), `Katu Minimal`, `Katu Dark` e `Katu Light`.
- Assinatura gráfica: linhas de rio e curvas de nível, em baixa intensidade, aplicadas com propósito em separadores, seleção e materiais institucionais.
- Evitar bandeiras literais, neon em excesso, slogans permanentes e elementos nacionais genéricos.

## Iconografia

Prioridade para arquivos, rede, áudio, bateria, dispositivos, configurações, terminal, navegador, instalador, atualização e energia. Preservar as metáforas universais. Padronizar grade, perspectiva, espessura, cantos, contraste e alinhamento. Entregar variantes de 16, 22, 32, 48, 64 e 128 px quando houver vetor/matriz adequada; não ampliar bitmap pequeno para fingir alta resolução.

## Aplicação por superfície

- **SDDM/bloqueio:** wallpaper adaptável, contraste controlado, usuário e autenticação como foco; hora e data secundárias; ações de energia com alvos confortáveis. A autenticação permanece inalterada.
- **Plasma:** paleta KatuDark coerente entre janela, menu, diálogo e notificação; KatuLight como alternativa visual.
- **Painel:** inferior, reconhecível e previsível; botão Katu, tarefas, bandeja e relógio com estados claros.
- **Dolphin e Configurações:** herdar superfícies, seleção, ícones e foco do tema, preservando funcionamento dos aplicativos.
- **Calamares:** mesmas cores, logo, tipografia e voz; indicar passo e ação com clareza. Só branding/slides/estilo visual podem mudar.
- **GRUB/Plymouth:** congelados por risco de boot nesta evolução inicial; não alterar entradas, parâmetros ou mecanismo.

## Acessibilidade

- Verificar contraste de texto e controles; manter foco de teclado visível em todas as telas próprias.
- Combinar texto, forma ou ícone aos estados de sucesso, aviso e erro.
- Garantir leitura com escala ampliada, acentos PT-BR, datas brasileiras e alvos de interação confortáveis.
- Não usar movimento para transmitir informação indispensável; respeitar movimento reduzido onde a plataforma oferece suporte.

## Tom de voz

Português brasileiro simples, direto e acolhedor. Preferir verbos claros e caixa de sentença. Erros devem explicar o que aconteceu e o próximo passo possível. Marca e slogans ficam em material institucional; controles dizem exatamente o que fazem.

## Regras de preservação

1. Não alterar scripts de build, boot, kernel, initramfs, systemd, Live, criação do usuário, montagem, SquashFS ou drivers.
2. Não alterar a sequência nem a lógica técnica do Calamares.
3. Não alterar GRUB/Plymouth nesta fase; seu visual será mantido se a mudança não puder ser isolada com segurança.
4. Comparar todo arquivo protegido com `KATU-GOLDEN-FUNCTIONAL.sha256` antes do build.
5. Uma regressão funcional sempre desfaz a alteração visual responsável.
