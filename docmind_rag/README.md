# CKP02 — DocMind RAG · Educação Financeira Pessoal

**Prompt Engineering & AI · FIAP · 2º Semestre 2026**
**Integrantes:** Fernando Hideki Rosa Oda (RM571408) · Léo Moreno Sambo (RM569556) · Thor Ferreira Camargo (RM569543) · Gabriel Botelho Romão (RM570589) · Rafael Marinucci Peres (RM569729) · David dos Reis Cardoso (RM568938)
**Peso: 30% · Apresentação: Aula 07 · Entrega: 23:59 do dia da Aula 08 (.zip via Teams — só o líder)**

Continuação do [CKP01](../README.md) — mesmo domínio e grupo. O pipeline RAG
construído aqui vira a base de uma `@tool` no CKP03.

## Domínio

Mesmo domínio do CKP01: **educação financeira pessoal** ("FinComigo"). Este
checkpoint constrói um pipeline RAG sobre uma base real de documentos
oficiais brasileiros sobre o tema — orçamento, dívidas, investimentos
(Tesouro Direto) e planejamento financeiro.

## Base de conhecimento

6 documentos oficiais reais, com fonte citada (ver [docs/FONTES.md](docs/FONTES.md)
para o detalhe e o histórico de correção de 2 URLs que estavam quebradas):

| Documento | Órgão | Páginas |
|---|---|---|
| Caderno de Educação Financeira — Gestão de Finanças Pessoais | Banco Central do Brasil | 98 |
| Guia de Planejamento Financeiro | CVM / investidor.gov.br | 18 |
| Guia de Boas Práticas de Educação Financeira no Setor Bancário | Febraban | 67 |
| Regulamento do Tesouro Direto | B3 / Tesouro Nacional | 36 |
| Guia do Investidor (Tesouro Direto) | ENAP | 11 |
| Reestruturação de Dívidas e Perfil do Endividamento do Cidadão (Estudo Especial nº 45/2019) | Banco Central do Brasil | 6 |

## Arquitetura

```
load (PyPDFLoader) → split (RecursiveCharacterTextSplitter, 2 configs)
   → embed (OllamaEmbeddings nomic-embed-text) → store (ChromaDB local)
   → retrieve (buscar()) → rerank opcional (cross-encoder) → generate (gemma4:cloud)
```

| Requisito | Status | Implementação |
|---|---|---|
| Pipeline RAG completo | ✅ | `app/document_loader.py` → `chunking.py` → `vectorstore.py` → `retrieval.py` → `generation.py`, orquestrado em `app/rag_pipeline.py` |
| 2 configurações de chunking | ✅ | `app/chunking.py` — `pequeno_512` (512/64) e `grande_1024` (1024/128) |
| nomic-embed-text | ✅ | `OllamaEmbeddings(model='nomic-embed-text')` em `app/vectorstore.py` |
| gemma4:cloud (generate) | ✅ | `ChatOllama(model='gemma4:cloud', temperature=0)` em `app/generation.py` |
| ChromaDB local | ✅ | `chromadb.PersistentClient()`, coleções `educacao_financeira_<config>` |
| Resposta cita a fonte | ✅ | Prompt de geração exige `[Fonte: nome_do_documento]` |
| RAGAS (faithfulness + answer_relevancy) | ✅ | `app/ragas_eval.py`, ≥5 perguntas por configuração |
| Função `buscar(consulta)` reaproveitável no CKP03 | ✅ | `app/retrieval.py` |
| Metadata filtering (diferencial) | ✅ | `buscar(..., where={...})` |
| Reranking (diferencial) | ✅ | `app/reranking.py`, `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Interface Gradio (diferencial) | ✅ | `app/main.py` |

## Comparação de chunking + RAGAS

Avaliação real com `gemma4:cloud` + `nomic-embed-text`, 5 perguntas de
teste (`app/ragas_eval.py`), média de 2 rodadas limpas contra as duas
coleções já indexadas com os 6 documentos:

| Config | chunk_size | overlap | Nº chunks | Faithfulness médio | Answer relevancy médio |
|---|---|---|---|---|---|
| pequeno_512 | 512 | 64 | 996 | 1,000 | 0,879 |
| grande_1024 | 1024 | 128 | 555 | 1,000 | 0,838 |

**Conclusão:** as duas configurações têm **faithfulness perfeito (1,000)** —
nenhuma resposta saiu do que estava nos documentos, bem acima da meta de
0,7 e da zona ideal de 0,9. No `answer_relevancy`, **`pequeno_512` venceu**
(0,879 vs 0,838): chunks menores, mesmo sendo quase o dobro em quantidade,
geram buscas mais precisas nesta base — um chunk de 512 caracteres tende a
focar num único subtema (ex: só "cuidados com cartão de crédito"), enquanto
um chunk de 1024 às vezes mistura dois parágrafos de assuntos adjacentes,
diluindo a relevância do que é recuperado. Por isso a coleção padrão usada
em `app/main.py` é `educacao_financeira_pequeno_512`.

### Nota sobre uma anomalia detectada e corrigida

Numa rodada inicial, `grande_1024` registrou `answer_relevancy = 0,000` na
pergunta sobre orçamento mensal — investigando, a resposta em si era boa e
fundamentada, mas começava com uma ressalva do tipo "o contexto não detalha
o passo a passo, mas...", que confundia o cálculo de relevância do RAGAS
(e também não é a melhor experiência para quem usa o chat). Ajustamos a
regra 2 do `SYSTEM_PROMPT` (`app/generation.py`) para responder direto
quando há informação relevante, reservando a ressalva só para quando não há
nada relevante no contexto — a tabela acima já reflete o resultado após
esse ajuste, confirmado em 2 rodadas limpas consecutivas.

## Diferenciais — evidência real

### Metadata filtering

Busca por "o que é Tesouro Direto?" sem e com filtro `where={"fonte":
"b3_regulamento_tesouro_direto"}`:

```
SEM filtro (top 4): enap_guia_investidor_tesouro, b3_regulamento_tesouro_direto,
                     enap_guia_investidor_tesouro, enap_guia_investidor_tesouro
COM filtro:          b3_regulamento_tesouro_direto (nos 4 resultados)
```

O filtro restringiu corretamente a busca a um único documento.

### Reranking

Busca por "quais os cuidados ao usar cartão de crédito?" — ordem antes e
depois do cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`):

```
ANTES (distância da busca vetorial):
1. dist=0.451 "(    ) O cartão de crédito pode ser uma alternativa..."
2. dist=0.469 "Maior cuidado ainda deve-se tomar para não se contratar..."
3. dist=0.500 "3.4 Uso do crédito..."

DEPOIS (score do cross-encoder):
1. score=3.312 "(    ) O cartão de crédito pode ser uma alternativa..."
2. score=2.525 "comerciais etc. É muito importante para sua vida financeira..."
3. score=2.247 "Maior cuidado ainda deve-se tomar para não se contratar..."
```

O reranking reordenou os candidatos — o chunk que era 4º lugar na busca
vetorial pura subiu para 2º depois do cross-encoder avaliar a relevância
real à pergunta.

### Interface Gradio

`app/main.py` — `gr.ChatInterface` rodando o pipeline completo (retrieve +
rerank + generate), com as fontes citadas ao final de cada resposta.

## Como executar

**Pré-requisitos** (testado com Python 3.12):

1. [Ollama](https://ollama.com) instalado, com o servidor local rodando
   (`ollama serve`, ou já em segundo plano) — é ele quem conversa com o
   Ollama Cloud e roda o modelo de embedding.
2. Autenticação com o Ollama Cloud, para o `gemma4:cloud`: `ollama signin`
   (ou exportar a `OLLAMA_API_KEY` no ambiente do processo `ollama serve`).
3. O modelo de embedding, que roda localmente: `ollama pull nomic-embed-text`.

```bash
cp .env.example .env   # edite com sua OLLAMA_API_KEY — este arquivo NÃO vai no .zip
pip install -r requirements.txt   # versões exatas testadas; o primeiro install é pesado (torch)

python -m app.main          # interface Gradio: http://localhost:7860
```

O índice vetorial já vem pronto na pasta `chroma_db/` (as 2 coleções, geradas
a partir dos 6 documentos de `docs/`), então **não é preciso reindexar** para
usar o chat. A primeira pergunta demora um pouco mais porque carrega o
cross-encoder de reranking (baixa o modelo do Hugging Face na primeira vez).

Só reindexe se adicionar documentos (ver abaixo) — demora alguns minutos
porque gera os embeddings de novo:
```bash
python -m scripts.indexar
```

Para rodar a avaliação RAGAS (usa a API do Ollama Cloud, leva alguns minutos):
```bash
python -m app.ragas_eval
```

## Como adicionar um documento novo à base

1. Baixar o PDF e salvar em `docs/`, com um nome de arquivo descritivo
   (ex: `orgao_titulo_do_documento.pdf`) — esse nome vira a `fonte` citada
   nas respostas.
2. Adicionar uma linha em `docs/FONTES.md` com título, órgão e URL de
   origem.
3. Rodar `python -m scripts.indexar` de novo — ele recria as 2 coleções do
   zero (apaga e reindexa tudo que está em `docs/`, incluindo o novo
   documento).
4. Conferir no log que o número de chunks indexados aumentou.

## Estrutura do projeto

```
docmind_rag/
├── app/
│   ├── __init__.py
│   ├── main.py              # Interface Gradio (diferencial) + entry point
│   ├── document_loader.py   # load
│   ├── chunking.py          # split (2 configurações)
│   ├── vectorstore.py       # embed + store (ChromaDB)
│   ├── retrieval.py         # retrieve — função buscar(consulta)
│   ├── reranking.py         # reranking (diferencial)
│   ├── generation.py        # generate, com citação de fonte
│   ├── rag_pipeline.py      # junta retrieve [+ rerank] + generate
│   ├── ragas_eval.py        # avaliação RAGAS
│   └── _ragas_compat.py     # shim p/ bug conhecido do ragas (ver docstring)
├── scripts/
│   └── indexar.py           # reindexação da base (load → split → embed → store)
├── docs/                     # os 6 documentos reais + FONTES.md
├── chroma_db/                 # índice ChromaDB pronto (gerado por scripts/indexar.py)
├── tests/                      # testes automatizados offline
├── .env.example
├── requirements.txt
└── README.md
```

## Testes automatizados

```bash
pytest tests/ -v
```

Cobrem o `RecursiveCharacterTextSplitter` (as 2 configurações, overlap na
faixa 10-15%, preservação de metadata) — rodam offline, sem chamar nenhum
modelo.

## Nota técnica: bug conhecido do pacote `ragas`

`ragas/llms/base.py` faz um import incondicional de
`langchain_community.chat_models.vertexai.ChatVertexAI`, submódulo que foi
removido do `langchain-community` (pacote em processo de "sunset" — ver
[issue #674](https://github.com/langchain-ai/langchain-community/issues/674)).
Isso quebra `import ragas` em qualquer ambiente moderno, mesmo sem usar
Vertex AI. `app/_ragas_compat.py` registra um stub mínimo em `sys.modules`
antes do import real, contornando o problema sem precisar da dependência do
Google Cloud (este projeto usa só Ollama). Ver o docstring do arquivo para
o detalhe.
