# CKP01 — Chatbot Profissional · Atendimento ao Cliente (E-commerce)

**Prompt Engineering & AI · FIAP · 2º Semestre 2026**
**Integrantes:** [Nome Completo (RM00000)] · [Nome Completo (RM00000)] · [Nome Completo (RM00000)]
**Peso: 25% · Apresentação: Aula 04 · Entrega: 23:55 do dia da Aula 05 (.zip via Teams — só o líder)**

## Domínio

Assistente virtual de atendimento ao cliente da loja fictícia de eletrônicos
"TechNova". O chatbot (persona "Ana") ajuda clientes com dúvidas sobre
produtos, status de pedidos, trocas/devoluções e reclamações.

Escolhido porque conversas de suporte são naturalmente multi-turno (o cliente
menciona um pedido/produto e retoma o assunto depois) e geram saídas
estruturadas claras (categoria, urgência, sentimento), além de servir de base
para RAG (catálogo/políticas) no CKP02 e para tools de um agente (consultar
pedido, calcular frete) no CKP03.

Usuários-alvo: clientes da loja online que buscam suporte pré ou pós-venda.

## Requisitos atendidos

| Requisito | Status | Implementação |
|---|---|---|
| Pipeline LCEL | ✅ | `app/chain.py` — `prompt \| llm \| PydanticOutputParser()` |
| ChatOllama | ✅ | `gemma4:cloud` via Ollama Cloud (`.env`) |
| Memória gerenciada | ✅ | `ConversationChain` + `ConversationTokenBufferMemory`, justificada em `app/memory_manager.py` |
| Pydantic v2 (≥4 campos) | ✅ | `AnaliseSolicitacao` com 6 campos em `app/schemas.py` |
| Context rot | ✅ | `app/context_rot.py` — tabela 0/5/10/15/20 turnos |
| Domínio documentado | ✅ | Este README + system prompt em `app/prompts.py` |

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

## Justificativa da memória

Escolhemos **`ConversationTokenBufferMemory`** (janela de ~1200 tokens). Em
atendimento ao cliente, detalhes exatos citados pelo usuário (número de
pedido, nome de produto) não podem ser parafraseados por um resumo — um
`SummaryMemory` correria o risco de distorcer esses dados. O `TokenBuffer`
mantém os turnos recentes de forma literal e descarta os mais antigos ao
ultrapassar o limite, o que garante fidelidade aos dados recentes e um teto
previsível de custo por chamada ao modelo (diferente do `BufferMemory` puro,
que cresce sem limite). Ver `app/memory_manager.py` para a implementação das
três estratégias.

## Estrutura do projeto

```
app/
├── __init__.py
├── main.py            # Interface Gradio + entry point
├── chain.py            # As 2 chains (conversa + LCEL estruturado)
├── memory_manager.py   # 3 estratégias de memória + a escolhida
├── schemas.py           # Pydantic v2 — AnaliseSolicitacao
├── context_rot.py       # Demonstração de degradação com contexto crescente
└── prompts.py            # System prompts com XML tagging
```

## Diferenciais (em progresso)

- [ ] Context engineering com métricas (tiktoken + gráfico) — `app/context_rot.py`
- [ ] Meta prompting (antes/depois do system prompt)
