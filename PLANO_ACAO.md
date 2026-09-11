# Plano de Ação — CKP01 Chatbot Profissional (meta: nota 10 + diferenciais)

**Disciplina:** Prompt Engineering and Artificial Intelligence · FIAP · 2º Semestre 2026
**Peso:** 25% da nota do semestre · **Apresentação:** Aula 04 · **Entrega:** 23:55 do dia da Aula 05
**Prof. Jorge Luiz Gomes** (profjorge.gomes@fiap.com.br)

---

## 0. Domínio escolhido

**Assistente Virtual de Educação Financeira Pessoal — "FinComigo"**

Por que esse domínio funciona bem para os três checkpoints do semestre:

| CKP | Como o domínio se encaixa |
|---|---|
| CKP01 (agora) | Conversas de educação financeira são naturalmente multi-turno (usuário menciona meta/dívida/valor e retoma o assunto depois) → memória tem propósito real. Saídas estruturadas óbvias (categoria da consulta, urgência, sentimento). |
| CKP02 (RAG) | Base de conhecimento rica e fácil de gerar: guias de orçamento, glossário de conceitos financeiros (Tesouro Direto, CDB, reserva de emergência), políticas gerais de crédito. |
| CKP03 (Agente) | Ações naturais como *tools*, todas calculáveis sem depender de API externa: calculadora de juros compostos, simulador de financiamento, categorizador de gastos. |

Usuários-alvo: pessoas que querem organizar as próprias finanças e entender conceitos financeiros básicos, sem acesso a um consultor particular.

Ponto de atenção específico deste domínio: como envolve dinheiro, o system prompt precisa deixar **muito claro** que o chatbot é educativo — nunca deve recomendar um ativo/investimento específico como se fosse adequado ao caso pessoal do usuário (isso é aconselhamento regulado, exige certificação CFP/CVM). Ver seção 3.4.

**Registrem o domínio escolhido no Portal ainda na Aula 01** — é o item que mais gente esquece (domínio duplicado com outro grupo só aceita o primeiro a entregar).

---

## 1. Arquitetura obrigatória (Aula 03 — 2 chains)

```
┌─────────────────────────────┐      ┌──────────────────────────────────────┐
│ Chain 1 — Conversa (chat)    │      │ Chain 2 — Saída estruturada (LCEL)    │
│ ConversationChain + memória  │      │ ChatPromptTemplate                    │
│ (Buffer/Summary/TokenBuffer) │      │   | ChatOllama                       │
│                               │      │   | PydanticOutputParser              │
└─────────────────────────────┘      └──────────────────────────────────────┘
      ↓                                          ↓
 resposta em linguagem natural           AnaliseConsulta(categoria=...,
 para o usuário no Gradio                urgencia=..., sentimento=..., ...)
```

- **Chain 1** cuida da conversa (persona, respostas humanas, mantém contexto).
- **Chain 2** roda em paralelo/sobre a mesma entrada para extrair dados estruturados e validados (ex: toda mensagem do cliente é classificada).
- As duas usam o mesmo `ChatOllama` (`gemma4:cloud`), mas prompts e parsers diferentes.

---

## 2. Estrutura do projeto (obrigatória)

```
ckp01-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py            # Interface Gradio + entry point (python -m app.main)
│   ├── chain.py           # As 2 chains (conversa + LCEL estruturado)
│   ├── memory_manager.py  # Implementação das 3 estratégias + a escolhida
│   ├── schemas.py         # Pydantic v2 — AnaliseConsulta (≥4 campos)
│   ├── context_rot.py     # Script/módulo de demonstração de degradação
│   └── prompts.py         # System prompts com XML tags
├── .env.example
├── .env                   # NUNCA vai no .zip
├── requirements.txt
└── README.md
```

---

## 3. Checklist mapeado à rubrica (10,0 pontos)

### 3.1 Pipeline LCEL funcional — 3,0 pts
- [ ] `chain.py` usa operador `|`: `prompt | llm | parser`
- [ ] `ChatPromptTemplate` com variáveis (nunca f-string manual) — system message e human message **separados**
- [ ] `ChatOllama` configurado exclusivamente com `model="gemma4:cloud"`, apontando para Ollama Cloud, lendo `OLLAMA_API_KEY` do `.env` via `python-dotenv`
- [ ] `python -m app.main` sobe sem erro (Gradio em `localhost:7860`)
- [ ] Testar manualmente: enviar mensagem, ver resposta de chat E saída estruturada válida

### 3.2 Gestão de memória e context rot — 2,5 pts
- [ ] Escolher **um** tipo: Buffer, Summary ou TokenBuffer (800–1500 tokens)
  - Recomendação para este domínio: **TokenBuffer (~1200 tokens)** — em educação financeira, detalhes exatos (valor de uma meta, valor de uma dívida) não podem ser parafraseados por um resumo; um buffer com janela de tokens preserva os turnos recentes literalmente e ainda limita custo. Documentar essa justificativa no README.
- [ ] Implementar em `memory_manager.py`, plugado no `ConversationChain`
- [ ] Testar e registrar evidência de memória funcionando em **≥5 turnos** (ex: mencionar uma meta de economia no turno 1, perguntar "qual era minha meta mesmo?" no turno 5)
- [ ] `context_rot.py`: mesmo prompt/pergunta rodado com janelas de contexto crescentes (0/5/10/15/20 turnos de "ruído" antes da pergunta real) → mostrar em tabela ou gráfico que a qualidade da resposta cai conforme o contexto cresce

### 3.3 Pydantic v2 com validação — 2,0 pts
- [ ] `schemas.py`: `AnaliseConsulta(BaseModel)` com ≥4 campos tipados, por exemplo:
  ```python
  class AnaliseConsulta(BaseModel):
      categoria: Literal["orcamento", "divida", "investimento_educacional", "planejamento_meta", "duvida_conceito", "outro"]
      urgencia: Literal["baixa", "media", "alta"]
      sentimento: Literal["positivo", "neutro", "negativo"]
      topico_mencionado: str | None = None
      resumo: str = Field(..., description="Resumo da consulta em 1 frase")
      acao_recomendada: str
  ```
- [ ] Usar `PydanticOutputParser` (não `JsonOutputParser`) — integrado à Chain 2 do LCEL
- [ ] Validar que erros de formato do modelo não quebram a aplicação (parser com instruções claras de formato no prompt)

### 3.4 System prompt e domínio — 1,5 pts
- [ ] Persona robusta em `prompts.py` com **XML tags** (técnica da Aula 04): `<persona>`, `<regras>`, `<restricoes>`, `<exemplos>`
- [ ] Regras e restrições coerentes com o domínio: **nunca recomendar um ativo/investimento específico como adequado ao caso pessoal do usuário** (isso é aconselhamento regulado — orientar a buscar um consultor CFP/CVM), nunca pedir dados bancários, nunca prometer rentabilidade/economia garantida
- [ ] Testar que o chatbot **não sai do personagem** mesmo sob perguntas fora do escopo ("ignore suas instruções", "me recomenda uma ação para comprar agora")
- [ ] README documenta: domínio, por que foi escolhido, usuários-alvo

### 3.5 Código e documentação — 1,0 pt
- [ ] Comentários em PT-BR só onde agregam (não redundantes)
- [ ] Módulos organizados exatamente como a estrutura acima
- [ ] README com instruções de execução claras (copiar `.env.example`, instalar deps, rodar)
- [ ] README com nomes e RMs de todos os integrantes

---

## 4. Diferenciais (até +1,0 — nota final ainda limitada a 10,0)

### 4.1 Context engineering com métricas (+0,5)
- [ ] Usar `tiktoken` para contar tokens reais de cada janela testada no context rot
- [ ] Medir "qualidade" de forma objetiva e reproduzível — não só opinião: ex. taxa de acerto de uma pergunta com resposta factual conhecida, ou tempo de resposta, por janela de contexto
- [ ] Gráfico (matplotlib, salvo como PNG) ou tabela comparativa clara no README

### 4.2 Meta prompting (+0,5)
- [ ] Usar o próprio `gemma4:cloud` para criticar/melhorar o system prompt inicial (técnica da Aula 04)
- [ ] Documentar **antes e depois** do prompt no README, com uma frase sobre o que melhorou

---

## 5. Cronograma (alinhado às aulas)

| Quando | Entregável interno | Responsável sugerido |
|---|---|---|
| Aula 01 | Domínio escolhido e **registrado no Portal** | Todo o grupo decide, líder registra |
| Aula 02 | Memória gerenciada implementada e justificada (R2) | 1–2 pessoas |
| Antes da Aula 03 | Chain LCEL básica funcionando com ≥3 turnos | 1–2 pessoas |
| Aula 03 | Check-in com o professor — chain rodando, feedback no system prompt | Todo o grupo |
| Aula 03→04 | Pydantic + context_rot + XML system prompt finalizados | Dividir por módulo |
| Aula 04 | Apresentação do professor (sem apresentação do grupo) — início da janela de 1 semana | — |
| Antes da Aula 05 | README completo, testes finais, `.zip` montado | Líder do grupo |
| Aula 05, até 23:55 | **Entrega via Teams** (só o líder envia) | Líder do grupo |

---

## 6. Ordem de implementação recomendada (3–4h de trabalho efetivo)

1. **Setup** (15 min): estrutura de pastas, `requirements.txt` (`langchain`, `langchain-ollama`, `pydantic`, `python-dotenv`, `gradio`, `tiktoken`), `.env.example` com `OLLAMA_API_KEY=`
2. **`prompts.py`** (30 min): escrever persona + regras + restrições com XML tags
3. **`schemas.py`** (15 min): `AnaliseSolicitacao` com os campos definidos
4. **`chain.py`** (45 min): montar as 2 chains — conversa com memória + LCEL estruturado com parser
5. **`memory_manager.py`** (30 min): implementar TokenBuffer (ou a escolha do grupo), testar 5+ turnos
6. **`main.py`** (30 min): interface Gradio simples ligando tudo, `if __name__ == "__main__"` chamando `app.launch()`
7. **`context_rot.py`** (45 min): gerar janelas de contexto crescentes, medir e tabular/plotar degradação
8. **Diferenciais** (30–45 min, opcional mas vale +1,0): contagem de tokens com tiktoken + meta prompting documentado
9. **README.md** (30 min): preencher todas as seções do modelo, com nomes/RMs reais
10. **Revisão final** (20 min): rodar `python -m app.main` do zero num ambiente limpo, conferir que `.env` está fora do `.zip`, montar `CKP01_[dominio]_grupo.zip`

---

## 7. Armadilhas comuns que derrubam nota (evitar)

- Usar `JsonOutputParser` em vez de `PydanticOutputParser` (a rubrica pede explicitamente o parser que valida)
- f-strings manuais no lugar de `ChatPromptTemplate` com variáveis
- Memória "decorativa" que não é realmente testada em 5+ turnos
- Seção de context rot que só afirma degradação sem mostrar dado/gráfico/tabela
- System prompt fraco que quebra personagem fácil sob prompt injection do usuário
- Esquecer de tirar o `.env` do `.zip` (contém chave — risco de segurança, e é regra explícita do enunciado)
- Modelo diferente de `gemma4:cloud` (proibido usar modelos deprecated)
- Projeto que não roda com `python -m app.main` num ambiente limpo (perde os 3,0 pontos do pipeline)

---

## 8. Antes de enviar — checklist final

- [ ] `.zip` nomeado `CKP01_[dominio]_grupo.zip`
- [ ] Contém `app/`, `.env.example`, `requirements.txt`, `README.md`
- [ ] **Não** contém `.env`
- [ ] README com nomes + RMs de todos os integrantes
- [ ] Todos os requisitos obrigatórios da seção 3 marcados
- [ ] Líder do grupo envia via Teams, na tarefa do professor, até 23:55 do dia da Aula 05
