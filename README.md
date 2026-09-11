# CKP01 — Chatbot Profissional · Educação Financeira Pessoal

**Prompt Engineering & AI · FIAP · 2º Semestre 2026**
**Integrantes:** Rafael Marinucci Peres (RM569729) · David dos Reis Cardoso (RM568938)
**Peso: 25% · Apresentação: Aula 04 · Entrega: 23:55 do dia da Aula 05 (.zip via Teams — só o líder)**

## Domínio

Assistente virtual de educação financeira da plataforma fictícia "FinComigo".
O chatbot (persona "Fê") ajuda usuários a organizar orçamento, entender
dívidas, planejar metas de economia e compreender conceitos de investimento —
sempre de forma educativa, nunca como recomendação personalizada de compra ou
venda de ativos (isso fica a cargo de um consultor certificado CFP/CVM).

Escolhido porque conversas de educação financeira são naturalmente
multi-turno (o usuário menciona uma meta, dívida ou valor e retoma o assunto
depois) e geram saídas estruturadas claras (categoria, urgência, sentimento),
além de servir de base para RAG (guias financeiros, glossário de conceitos)
no CKP02 e para tools de um agente (calculadora de juros compostos, simulador
de financiamento, categorizador de gastos) no CKP03.

Usuários-alvo: pessoas que querem organizar as próprias finanças e entender
conceitos financeiros básicos, sem acesso a um consultor particular.

## Requisitos atendidos

| Requisito | Status | Implementação |
|---|---|---|
| Pipeline LCEL | ✅ | `app/chain.py` — `prompt \| llm \| PydanticOutputParser()` |
| ChatOllama | ✅ | `gemma4:cloud` via Ollama Cloud (`.env`) |
| Memória gerenciada | ✅ | `ConversationChain` + `ConversationTokenBufferMemory`, justificada em `app/memory_manager.py` |
| Pydantic v2 (≥4 campos) | ✅ | `AnaliseConsulta` com 6 campos em `app/schemas.py` |
| Context rot | ✅ | `app/context_rot.py` — tabela 0/5/10/15/20 turnos |
| Domínio documentado | ✅ | Este README + system prompt em `app/prompts.py` |

## Interface e tema

A interface usa `gr.ChatInterface` (Gradio) com um tema escuro customizado
(`app/theme.py`), paleta inspirada no design system da Binance (canvas quase
preto + amarelo como único acento de marca — ver
`.claude/skills/binance-frontend-design/` para o guia de estilo completo).
O ícone em `app/assets/icon.png` (fundo removido, PNG transparente) é usado
como favicon da aba do navegador e como avatar da Fê nas mensagens do chat.
`gr.ChatInterface` também entrega, de graça, exemplos de pergunta clicáveis,
botões de copiar/regenerar resposta e rolagem automática — um visual mais
próximo de um chat de produto (Claude, ChatGPT) do que uma tela genérica.

**Nota de compatibilidade:** o Gradio 6 removeu o formato antigo de mensagens
em tupla do `Chatbot` — mensagens agora precisam ser dicionários
`{"role": ..., "content": ...}`. Também moveu `theme`/`css` do construtor de
`Blocks()` para `demo.launch()`. `app/main.py` já reflete as duas mudanças.

## Como executar (local — sem Colab)

```bash
cp .env.example .env   # edite com sua OLLAMA_API_KEY — este arquivo NÃO vai no .zip
pip install -r requirements.txt
python -m app.main     # Gradio: http://localhost:7860
```

Para rodar a demonstração de context rot isoladamente:

```bash
python -m app.context_rot
```

## Testes automatizados

```bash
pytest tests/ -v
```

Os testes usam um modelo falso (`FakeChatModel`) no lugar do `ChatOllama` real,
então rodam offline e não gastam tokens. Cobrem: validação do schema Pydantic
(`tests/test_schemas.py`), as 3 estratégias de memória e a retenção/descarte
de turnos no `TokenBufferMemory` (`tests/test_memory_manager.py`), e a fiação
das 2 chains — inclusive que a `ConversationChain` lembra de um dado citado em
turnos anteriores e que a Chain 2 retorna um `AnaliseConsulta` válido
(`tests/test_chain.py`).

**Nota:** `ConversationChain` e as classes de memória (`ConversationBufferMemory`,
`ConversationSummaryMemory`, `ConversationTokenBufferMemory`) foram movidas
para o pacote `langchain-classic` a partir do LangChain 1.0 e emitem um
`DeprecationWarning` (serão substituídas por `create_agent` no LangChain 2.0).
Isso é esperado e não é um erro — usamos essas classes porque são a
arquitetura exigida no enunciado (Aula 03).

## Justificativa da memória

Escolhemos **`ConversationTokenBufferMemory`** (janela de ~1200 tokens). Em
educação financeira, detalhes exatos citados pelo usuário (valor da meta,
valor da dívida, prazo) não podem ser parafraseados por um resumo — um
`SummaryMemory` correria o risco de distorcer esses números. O `TokenBuffer`
mantém os turnos recentes de forma literal e descarta os mais antigos ao
ultrapassar o limite, o que garante fidelidade aos dados recentes e um teto
previsível de custo por chamada ao modelo (diferente do `BufferMemory` puro,
que cresce sem limite). Ver `app/memory_manager.py` para a implementação das
três estratégias.

### Evidência real (6 turnos, `gemma4:cloud`)

```
Turno 1 — Usuário: Oi, minha meta é economizar R$500 por mês para viajar.
Turno 2 — Usuário: O que é melhor, Tesouro Direto ou poupança?
Turno 3 — Usuário: Estou também com uma dívida de R$2000 no cartão de crédito.
Turno 4 — Usuário: Qual das duas coisas eu deveria priorizar primeiro?
Turno 5 — Usuário: Qual era a minha meta de economia mensal mesmo, que eu falei no começo?
          Fê: "Sua meta é economizar R$ 500 por mês para viajar! [...]"   ✅ lembrou
Turno 6 — Usuário: E o valor da minha dívida no cartão, você lembra?
          Fê: "Lembro sim! Você mencionou que tem uma dívida de R$ 2.000 [...]"  ✅ lembrou
```

A memória reteve corretamente dois dados diferentes (meta de economia e valor
da dívida) citados em turnos distintos, mesmo com outros assuntos no meio.

## Estrutura do projeto

```
app/
├── __init__.py
├── main.py            # Interface Gradio (ChatInterface) + entry point
├── theme.py             # Tema visual (paleta inspirada no design system da Binance)
├── assets/
│   └── icon.png          # Favicon + avatar da Fê (fundo removido)
├── chain.py            # As 2 chains (conversa + LCEL estruturado)
├── memory_manager.py   # 3 estratégias de memória + a escolhida
├── schemas.py           # Pydantic v2 — AnaliseConsulta
├── context_rot.py       # Demonstração de degradação com contexto crescente
└── prompts.py            # System prompts com XML tagging
```

## Diferenciais (em progresso)

- [ ] Context engineering com métricas (tiktoken + gráfico) — `app/context_rot.py`
- [ ] Meta prompting (antes/depois do system prompt)
