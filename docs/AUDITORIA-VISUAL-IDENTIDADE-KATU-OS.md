# Auditoria visual e evolução da identidade do Katu OS

**Escopo:** somente identidade, interface e apresentação visual. Esta auditoria não avalia inicialização, instalação, segurança, desempenho ou outros aspectos funcionais.

**Base observada:** arquivos de marca, tema Plasma, layout do painel, tema de login SDDM, telas do Calamares e capturas de tela já salvas em `output/audit-20260923/`. A captura do desktop (`desktop-awake.png`) mostra Plasma em 1280 × 720; a captura de login (`login-current.png`) mostra o usuário “Katu Live”. As capturas são evidência visual do ambiente de teste e não uma inspeção ao vivo do computador do usuário.

## Diagnóstico executivo

O Katu OS já tem matéria-prima para uma identidade própria: nome de origem indígena, onça-pintada, Amazônia, rios, mapa do Brasil, assinatura “Livre. Brasileiro. Para todos.”, logotipo próprio, fundos temáticos, tema escuro e verde de destaque. O desafio principal é transformar esse conjunto de peças em uma experiência coesa e legível em todas as telas. Hoje, a identidade aparece com força nos fundos e nas telas de marca, mas perde consistência nas interfaces do desktop, no enquadramento em diferentes resoluções e na hierarquia visual.

Minha direção recomendada é **“Brasil contemporâneo, natureza viva, tecnologia para todos”**: usar a onça e as paisagens como símbolos editoriais pontuais, rios e linhas topográficas como assinatura gráfica recorrente, e uma interface sóbria que deixe o conteúdo respirar. A brasilidade deve vir de formas, cores, linguagem e referências visuais específicas, sem transformar cada tela em uma bandeira ou em um painel de slogans.

## O que já existe

- Logotipos escuro, branco e monocromático em `branding/logos/`.
- Seis papéis de parede Katu em `wallpapers/`, incluindo Amazônia, onça, rio, verde, escuro e minimalista.
- Paletas Plasma escura e clara em `plasma/colors/`.
- Layout Plasma com painel inferior, menu Kickoff, tarefas, bandeja e relógio em `plasma/look-and-feel/org.katuos.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`.
- Tema de login SDDM com logo, relógio, campo de senha, mensagens e ações de energia em `sddm/katu/Main.qml`.
- Tela de boas-vindas e seis slides do Calamares em `installer/calamares/branding/katu/`.
- Identidade de inicialização Plymouth e splash de sessão Plasma.
- Pacote de recursos adicionais em `imagens/katu-os-final-assets/`, com ícones, arte de boot, boas-vindas e logos.

## Achados visuais

### 1. O enquadramento ainda não é seguro em todas as telas

O tema SDDM declara uma tela de 1920 × 1080 diretamente no `Main.qml`. Os fundos usam `PreserveAspectCrop`, que recorta a imagem para preencher telas com outra proporção. Na captura de login em 1024 × 768, parte da marca aparece cortada junto à borda direita. Na captura do desktop em 1280 × 720, os textos integrados ao wallpaper também ficam parcialmente para fora das laterais. Logos e chamadas importantes não devem depender de coordenadas fixas nem ficar embutidos nas áreas periféricas do fundo.

**Evolução:** dimensionar os componentes pelas dimensões reais da tela; criar margens seguras; reposicionar ou reduzir elementos em telas 4:3, 16:10 e 16:9; testar também escala de interface ampliada. Manter logotipo e textos de interface como componentes independentes do wallpaper.

### 2. O desktop mistura uma marca escura com superfícies claras

Na captura `desktop-awake.png`, o fundo e os elementos da marca são escuros, mas o Dolphin e outras janelas exibidas aparecem com grandes áreas brancas e aparência Breeze clara. O repositório fornece `KatuDark.colors`, mas a configuração de aparência mantém `widgetStyle=Breeze`, e há valores com aparência de tema padrão. O resultado reduz a sensação de produto integrado e pode causar desconforto visual à noite.

**Evolução:** definir e validar um tema escuro completo para janelas, campos, listas, menus, caixas de diálogo, seleção, barras de rolagem e notificações. Oferecer o tema claro Katu como alternativa explícita. Fazer as duas variantes compartilharem a mesma paleta de marca e estados de interação.

### 3. O wallpaper tenta fazer papel de interface

Alguns fundos já incluem palavras, chamadas e o logotipo em posições próximas às bordas. Ícones, janelas e painel passam por cima dessa arte; o recorte muda conforme a resolução e pode cortar justamente as mensagens. Isso torna o desktop dependente de um cenário específico e compete com o conteúdo de trabalho.

**Evolução:** separar os papéis de parede limpos, sem texto e com áreas de baixa informação atrás de ícones e janelas, das telas promocionais usadas em apresentação, instalação e divulgação. Manter o logo da interface no painel, no menu e nas telas de sistema, em locais previsíveis.

### 4. A assinatura gráfica ainda não está organizada como sistema

As peças existentes usam onça, floresta, rio, mapa do Brasil, linhas verdes, slogans e diferentes composições. São referências fortes, porém falta uma regra visual que explique quando cada elemento aparece. O verde intenso `#00c853` também domina muitos controles e pode competir com as imagens; o âmbar `#ffab00` está documentado, mas pouco estruturado como cor de função.

**Evolução:** criar uma biblioteca concisa com logo principal e símbolo, versões claro/escuro, área de proteção, tamanhos mínimos, fundos permitidos, tipografia, ícones e paleta por função. Escolher uma assinatura visual repetível — linhas inspiradas no curso dos rios amazônicos, combinadas com curvas topográficas — e usá-la com contenção em divisores, seleção e telas institucionais. Não distorcer nem recolorir a onça/logotipo para usos decorativos.

### 5. A paleta está definida, mas precisa de regras de contraste e função

O tema escuro usa `#0d1117` para fundo, `#161b22` para superfícies, `#e6edf3` para texto e `#00c853` para destaque. É uma base consistente. Ainda falta documentar onde entram o âmbar, os tons de verde de superfície, links, estados de sucesso/aviso/erro e uma alternativa clara. O verde brilhante como texto pequeno ou traço fino pode perder legibilidade, sobretudo em telas de baixa qualidade.

**Evolução:** estabelecer tokens nomeados para fundo, superfície, borda, texto principal/secundário, foco, seleção, link, sucesso, aviso e erro. Reservar o verde vivo para ações e foco bem visíveis; usar um verde mais claro para texto sobre fundo escuro; testar contraste para texto normal e estados de foco. Usar âmbar para atenção e calor visual, não como segundo destaque permanente.

### 6. O painel inferior existe, mas não define sozinho a navegação

O layout do Plasma coloca o Kickoff, tarefas, bandeja e relógio no rodapé, atendendo à intenção de ter o menu sempre visível. A identidade do menu, espaçamento, ícone do Katu, separação entre aplicações abertas e indicadores de sistema precisa ser conferida em resoluções menores e com janelas maximizadas. No material disponível, não há uma captura limpa e recente do desktop mostrando o painel desobstruído.

**Evolução:** consolidar um painel inferior com altura confortável, botão Katu claramente reconhecível e rótulo acessível, ícones consistentes, tarefas com indicação legível da janela ativa e bandeja sem excesso. Avaliar um tratamento translúcido discreto, mantendo opacidade suficiente para leitura. Definir comportamento de ocultação e áreas de clique com base em telas de laptop e VirtualBox.

### 7. Os ícones próprios ainda parecem uma coleção parcial

Há ícones Katu para computador, home, rede, unidades removíveis e lixo, além de arquivos para alguns aplicativos Katu. O conjunto listado não demonstra cobertura equivalente para categorias de aplicações, ações comuns, estados, tipos de arquivo e dispositivos. Um desktop com poucos ícones próprios tende a voltar visualmente ao tema Breeze e enfraquecer a marca.

**Evolução:** mapear os ícones de sistema usados com maior frequência e completar a cobertura antes de tentar substituir todo o tema KDE. Definir grade, espessura de traço, perspectiva, cantos, cores e versões 16/22/32/48/64/128 px. Preservar metáforas universais — pasta, rede, lixeira — e aplicar o desenho Katu de forma consistente.

### 8. O login tem uma boa base, mas precisa de adaptação e revisão tipográfica

O SDDM tem logo, data, avatar, entrada de senha e ações para energia. O painel central usa dimensões fixas de 360 × 420, e o arquivo fixa a raiz em 1920 × 1080. Isso merece revisão para resoluções pequenas, proporções diferentes e escalas maiores. A captura do login/lockscreen mostra o fundo muito escurecido; o wallpaper e o wordmark perdem presença. A tela de bloqueio deve continuar reconhecível sem comprometer contraste do formulário.

**Evolução:** usar layout adaptativo, garantir que o campo e as ações não saiam da área visível, aumentar o tamanho mínimo dos alvos e tornar o erro de senha claro sem deslocar todo o painel. Ajustar a camada escura por imagem e checar o logo em telas de brilho reduzido. Manter o relógio informativo, mas secundário ao acesso.

### 9. A instalação tem identidade, mas pode ser mais clara e menos promocional

O Calamares já usa nome, slogan, logo, slides e cores Katu. Os textos dão boas-vindas, mas frases como “pronto para usar” e estimativas de tempo não devem competir com os passos e decisões da instalação. O usuário precisa reconhecer o progresso, o passo atual e as ações principais mesmo quando a janela está redimensionada.

**Evolução:** usar as imagens de slides como narrativa curta sobre origem, liberdade, comunidade e uso cotidiano no Brasil; limitar texto em cada slide; manter contraste e leitura em janela pequena; destacar passo atual e botão principal sem depender só da cor; usar a mesma tipografia, logotipo e tom de voz do login.

### 10. O idioma visual precisa acompanhar o PT-BR

O sistema busca falar com pessoas sem experiência prévia, mas a identidade não é só tradução. Menus, nomes, mensagens de erro, data, atalhos, instruções da instalação e ações do desktop devem formar uma linguagem única, simples e brasileira. Termos técnicos inevitáveis podem ter uma explicação curta no contexto.

**Evolução:** revisar a interface para PT-BR com frase curta, caixa de sentença e verbos consistentes. Usar data e hora brasileiras, acentos corretos e termos familiares. Evitar slogans em locais onde uma instrução direta ajuda mais.

### 11. Acessibilidade visual precisa fazer parte da marca

Os componentes usam principalmente texto pequeno, verde de destaque e estados hover. Isso não basta para pessoas com baixa visão, daltonismo, navegação por teclado ou preferência por menos movimento. Uma identidade forte também deve continuar utilizável quando o usuário aumenta fonte, escala e contraste.

**Evolução:** validar contraste de texto e ícones, escala em 125–200%, foco de teclado evidente, alvos clicáveis confortáveis, estados que não dependam apenas de verde/vermelho e respeito à preferência por movimento reduzido. Garantir que o login e o painel continuem legíveis em 1024 × 768.

## Direção visual recomendada

| Papel | Direção proposta |
|---|---|
| Fundo principal | Grafite profundo `#0d1117`, já presente, com opção clara quente e neutra para leitura prolongada. |
| Superfície | `#161b22` e variações com separação nítida de janelas e menus. |
| Cor de ação | Verde Katu `#00c853`, usado para foco, seleção e ação principal, após validação de contraste. |
| Cor de atenção | Âmbar `#ffab00`, aplicado a avisos e pequenos acentos. |
| Cores de identidade | Tons de mata, água e luz de fim de tarde como cores secundárias das artes, sem transformar a bandeira nacional em tema literal. |
| Tipografia | Manter Noto Sans como base por legibilidade e cobertura PT-BR; definir escala e pesos consistentes. Usar uma face de exibição apenas em material institucional, nunca em controles. |
| Assinatura | Curso de rio / curva topográfica como detalhe gráfico Katu; onça e paisagem como imagem editorial, não como textura em todas as telas. |
| Tom de voz | Direto, acolhedor e brasileiro: dizer o que a ação faz e como recuperar um erro. |

## Plano de evolução por prioridade

### Prioridade visual 1 — corrigir as inconsistências percebidas

1. Adaptar login e telas de marca a 1024 × 768, 1280 × 720 e 1920 × 1080, sem cortes laterais.
2. Revisar o enquadramento de todos os wallpapers e retirar textos embutidos dos fundos usados no desktop.
3. Fazer janelas, menus, notificações e diálogos respeitarem a paleta KatuDark; revisar a seleção de `widgetStyle` e a aplicação efetiva do esquema.
4. Validar a leitura do painel inferior com janelas maximizadas e em escala de interface ampliada.

### Prioridade visual 2 — dar unidade ao produto

1. Publicar uma folha de estilo da marca com logo, símbolo, cores funcionais, tipografia e áreas de proteção.
2. Aplicar os mesmos componentes de foco, botões, campos, cartões e mensagens a SDDM, boas-vindas e telas próprias.
3. Completar os ícones de maior frequência e alinhar o estilo dos ícones do menu e da bandeja.
4. Dar ao Calamares uma sequência visual de slides e ilustrações coerentes com a história brasileira do Katu OS.

### Prioridade visual 3 — acabamento de destaque

1. Criar uma família curta de wallpapers: um padrão com onça, um de rio, um minimalista e uma variante clara, todos sem texto e com áreas de trabalho livres.
2. Criar uma abertura institucional breve para materiais de apresentação, fora do fluxo normal de trabalho.
3. Projetar pequenos detalhes de sistema — seleção, divisores, estados e ilustrações — com o motivo visual de rios e relevo.
4. Revisar sons e animações apenas quando reforçarem uma ação ou retorno; oferecer redução de movimento.

## Critérios de aceite visual

- Nenhum logo, controle ou texto de interface cortado em 1024 × 768, 1280 × 720 e 1920 × 1080.
- Desktop reconhecível como Katu mesmo com uma janela maximizada, sem depender de slogans no wallpaper.
- Janelas de sistema, menus e painel com tema escuro coerente; tema claro utilizável como alternativa.
- Painel inferior visível, com menu e tarefas compreensíveis, foco e estado ativo distinguíveis sem depender somente da cor.
- Tela de login legível em baixa resolução, com campo, erro e opções de energia acessíveis.
- Calamares identificável como Katu sem comprometer leitura, progresso e clareza dos botões.
- Texto em PT-BR consistente, com fonte legível e ampliação sem sobreposição.
- A assinatura brasileira comunica-se por referências próprias — onça, floresta, água, luz e linguagem — com uso equilibrado e contemporâneo.

## Arquivos consultados

- `README.md`
- `branding/logos/` e `wallpapers/`
- `plasma/colors/KatuDark.colors` e `KatuLight.colors`
- `plasma/look-and-feel/org.katuos.desktop/contents/defaults`
- `plasma/look-and-feel/org.katuos.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`
- `plasma/look-and-feel/org.katuos.desktop/contents/splash/Splash.qml`
- `sddm/katu/Main.qml` e `sddm/katu/background.jpg`
- `installer/calamares/branding/katu/branding.desc`, `show.qml` e recursos da marca
- Capturas existentes em `output/audit-20260923/`, em especial `desktop-awake.png`, `login-current.png` e telas do instalador

