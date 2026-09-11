---
name: binance-frontend-design
description: Design system for any front-end/UI work on this project (FinComigo chatbot and its future React site for CKP02/CKP03) — a Binance-inspired dark canvas with a single yellow accent. Use whenever building or restyling a website, landing page, dashboard, or app UI (React, plain HTML/CSS, or a Gradio/Streamlit theme) for this repo, or when asked for "o tema", "o site", "o front-end", "a landing page" for FinComigo.
---

# Design de front-end — FinComigo (inspirado na Binance)

Sistema de design para qualquer interface deste projeto: o tema do Gradio
atual (`app/theme.py`) e qualquer site/front-end futuro (ex: a versão React
que pode nascer no CKP02/CKP03, quando o chatbot ganha RAG e depois um
agente). A referência completa (paleta, tipografia, componentes, grid,
responsividade) está em `references/design-tokens.md` — carregue esse
arquivo antes de implementar qualquer tela nova ou tema.

## Quando usar

- Criar ou restilizar uma página web, dashboard ou landing page para o
  FinComigo.
- Montar um tema (Gradio, Streamlit, CSS puro, Tailwind, styled-components)
  para este projeto.
- Decidir cores, tipografia, raio de borda, espaçamento ou componentes de UI
  (botões, cards, inputs, tabelas) para qualquer tela do produto.

## Ideia central

Canvas quase preto (`#0b0e11`) carrega tudo. **Um único acento de marca** —
o amarelo `#fcd535` — faz todo o trabalho visual: botão primário, headline de
destaque, badge, link. Não existe segunda cor de marca. É a escassez do
amarelo que dá poder a ele — nunca usar como cor de fundo grande ou em texto
corrido.

## Paleta essencial (ver `references/design-tokens.md` para a lista completa)

| Papel | Token | Hex |
|---|---|---|
| Canvas (fundo da página) | `canvas-dark` | `#0b0e11` |
| Card / superfície elevada | `surface-card-dark` | `#1e2329` |
| Superfície elevada (nível 2) | `surface-elevated-dark` | `#2b3139` |
| Acento de marca (botão primário, headline) | `primary` | `#fcd535` |
| Acento em hover/press | `primary-active` | `#f0b90b` |
| Texto no acento (botão amarelo) | `on-primary` | `#181a20` (preto) |
| Texto padrão sobre o canvas escuro | `body` | `#eaecef` |
| Texto secundário/legenda | `muted` | `#707a8a` |
| Hairline/borda sobre fundo escuro | `hairline-on-dark` | `#2b3139` |
| Positivo (ex: meta atingida, saldo positivo) | `trading-up` | `#0ecb81` |
| Negativo (ex: dívida, alerta) | `trading-down` | `#f6465d` |

Para telas transacionais (ex: um formulário de simulação financeira, "confirme
seus dados") considere inverter para canvas claro (`#ffffff`) com os mesmos
CTAs amarelos e hairlines cinza-azulados — é o padrão que a Binance usa em
telas de compra/depósito. Ver seção "Colors → Surface" da referência.

## Tipografia

BinanceNova/BinancePlex são fontes proprietárias da Binance — **não usar**
essas fontes diretamente. Substitutos abertos:
- Texto editorial (headlines, corpo, botões) → **Inter**
- Números (preços, valores em R$, percentuais, contadores) → **JetBrains
  Mono** ou **IBM Plex Sans**

Headlines usam peso 700 (mais pesado que sites de marketing genéricos) —
números precisam ser lidos rápido, então não suavizar para peso 400.

## Formas e espaçamento

- Raio de borda: `6px` em botões/inputs primários, `8px` em cards de
  conteúdo, `12px` em cards elevados, `pill` (borda total) só em CTAs de
  destaque máximo (ex: "Começar agora").
- Espaçamento em múltiplos de 4px; seções principais separadas por `80px`.
- Sem gradientes atmosféricos, sem glassmorphism. Profundidade vem do
  contraste entre `canvas-dark` e `surface-card-dark`, não de sombra.

## Regras que não podem quebrar

1. Botão primário = fundo amarelo + texto **preto** (`on-primary`), nunca
   texto branco no amarelo — perde a identidade visual.
2. Verde/vermelho (`trading-up`/`trading-down`) são sinais semânticos (valor
   positivo/negativo, meta atingida/dívida) — nunca usar como "sucesso
   genérico" ou cor de fundo de botão comum.
3. Um único acento de marca. Não introduzir uma segunda cor "de destaque" —
   se precisar de uma segunda cor, ela é neutra (cinza-azulado), não outra
   cor viva.
4. Números sempre na fonte/peso tabular (JetBrains Mono/IBM Plex Sans);
   texto corrido sempre em Inter. Não misturar.

## Ao implementar

1. Carregue `references/design-tokens.md` para os componentes específicos
   (botões, cards, tabelas, nav, formulários) e a tabela completa de
   tipografia/espaçamento/breakpoints antes de escrever CSS ou JSX.
2. Se for React: extraia os tokens acima como variáveis CSS
   (`:root { --color-primary: #fcd535; ... }`) ou um objeto de tema
   (styled-components/Tailwind config) em vez de hardcodar hex nos
   componentes.
3. Se for uma tela nova de dados financeiros do usuário (saldo, metas,
   dívidas), use o padrão `markets-row`/`price-up-cell`/`price-down-cell` da
   referência como modelo de tabela — valores positivos em verde, negativos
   em vermelho, sempre como cor de texto, nunca como fundo do card inteiro.
4. Teste em pelo menos 3 breakpoints (mobile < 768px, tablet 768–1024px,
   desktop > 1024px) — ver seção "Responsive Behavior" da referência.
