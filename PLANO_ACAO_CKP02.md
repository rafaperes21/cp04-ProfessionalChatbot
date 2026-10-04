# Plano de Ação — CKP02 DocMind RAG (meta: nota 10 + diferenciais)

**Disciplina:** Prompt Engineering and Artificial Intelligence · FIAP · 2º Semestre 2026
**Peso:** 30% da nota do semestre · **Apresentação:** Aula 07 (só o professor, sem apresentação do grupo) · **Entrega:** 23:59 do dia da Aula 08
**Prof. Jorge Luiz Gomes** (profjorge.gomes@fiap.com.br)

Este CKP é a continuação do [CKP01](PLANO_ACAO.md) — **mesmo domínio, mesmo grupo**
("educação financeira pessoal — FinComigo"). O pipeline RAG daqui vira uma
`@tool` do agente no CKP03, então vale investir em qualidade agora.

> **Nota:** o PDF original do enunciado menciona entrega via Colab, mas o
> professor confirmou em aula que isso foi um erro/confusão dele — **a
> entrega é igual ao CKP01: projeto Python local + `.zip` via Teams**, sem
> notebook. Este plano já reflete a correção. Ver o
> [plano em etapas detalhado](PLANO_ACAO_CKP02_ETAPAS.md) para a execução
> passo a passo.

---

## 0. Igual ao CKP01, mesma estrutura de projeto

Como no CKP01, o projeto é um **pacote Python local, sem notebook**,
organizado como `app/`, com `README.md`, `requirements.txt` e `.env.example`
na raiz, zipado e enviado via Teams no fim. A estrutura recomendada está na
seção 2 abaixo.

---

## 1. Base de conhecimento real (≥5 documentos, obrigatório)

**Atenção:** documentos fictícios ou sem fonte citada **zeram** o critério
"Qualidade da base de conhecimento" (2,0 pts). Abaixo, 5 fontes reais e
oficiais já localizadas, cobrindo as categorias do chatbot do CKP01
(orçamento, dívida, investimento, planejamento de meta):

| # | Documento | Órgão | Cobre |
|---|---|---|---|
| 1 | [Caderno de Educação Financeira — Gestão de Finanças Pessoais](https://www.bcb.gov.br/content/cidadaniafinanceira/documentos_cidadania/Cuidando_do_seu_dinheiro_Gestao_de_Financas_Pessoais/caderno_cidadania_financeira.pdf) | Banco Central do Brasil | Orçamento, uso de crédito, consumo, poupança/investimento, prevenção de riscos (98 pág.) |
| 2 | [Guia de Planejamento Financeiro](https://www.gov.br/investidor/pt-br/educacional/publicacoes-educacionais/guias/guia-de-planejamento-financeiro/guia-planejamento-financeiro.pdf) | CVM / investidor.gov.br | Planejamento de metas financeiras |
| 3 | [Guia do Investidor (Tesouro Direto)](https://repositorio.enap.gov.br/bitstream/1/6248/1/Guia_Investidor%20TD.pdf) | ENAP | Conceitos de investimento em renda fixa (Tesouro Direto) |
| 4 | [Guia de Boas Práticas de Educação Financeira no Setor Bancário](https://cmsarquivos.febraban.org.br/Arquivos/documentos/PDF/febraban-guia%20de%20boas%20pr%C3%A1ticas-v7-web.pdf) | Febraban | Práticas de educação financeira do setor bancário |
| 5 | [Regulamento do Tesouro Direto](https://www.b3.com.br/data/files/1B/D6/29/4F/22EC46101305DC46AC094EA8/Regulamento_Tesouro_Direto.pdf) | B3 / Tesouro Nacional | Conceitos de investimento em renda fixa (Tesouro Direto) |

> **Atualizado em 04/10/2026** após baixar e verificar de verdade: a URL
> antiga do caderno BCB redireciona para a nova acima, e o livro "TOP —
> Planejamento Financeiro Pessoal" (URL original do enunciado) estava
> quebrado (404), substituído pelo Guia do Investidor da ENAP. Ver
> `docmind_rag/docs/FONTES.md` para o detalhe.

**Antes de usar:** abrir cada link e confirmar que ainda carrega (são sites
de governo/instituição, podem reorganizar URLs) — se algum quebrar, procurar
o documento atualizado no mesmo domínio (`bcb.gov.br`, `gov.br/investidor`,
`febraban.org.br`, `b3.com.br`). Baixar os PDFs e **citar a fonte (URL +
órgão) no notebook**, como pede o enunciado.

Isso já cobre o mínimo de 5. Se quiserem mais riqueza (ajuda no critério de
"base rica o suficiente para perguntas não-triviais"), dá pra somar algo da
Serasa/SPC sobre negociação de dívidas — mas são páginas de blog comercial,
não PDF oficial, então tratar como complementar, não substituir os 5 acima.

---

## 2. Arquitetura obrigatória

```
load (PDFs) → split (RecursiveCharacterTextSplitter) → embed (nomic-embed-text)
   → store (ChromaDB) → retrieve (top-k + metadata) → generate (gemma4:cloud)
```

### Estrutura do projeto (local, igual ao espírito do CKP01)

```
docmind_rag/
├── app/
│   ├── __init__.py
│   ├── main.py              # Interface Gradio (diferencial) + entry point
│   ├── document_loader.py   # load: carrega os PDFs de docs/
│   ├── chunking.py          # split: RecursiveCharacterTextSplitter, 2 configs
│   ├── vectorstore.py       # embed + store: OllamaEmbeddings + ChromaDB
│   ├── retrieval.py         # retrieve: função buscar(consulta) + reranking
│   ├── generation.py        # generate: gemma4:cloud, prompt com citação de fonte
│   ├── rag_pipeline.py      # junta tudo: load→split→embed→store→retrieve→generate
│   └── ragas_eval.py        # avaliação RAGAS (faithfulness + answer_relevancy)
├── docs/                     # os 5 PDFs reais da base de conhecimento
├── chroma_db/                 # persistência do ChromaDB (gerado localmente, no .gitignore)
├── tests/                      # testes automatizados (chunking, schemas, etc — opcional mas recomendado)
├── .env.example
├── requirements.txt
└── README.md
```

Pontos não-negociáveis do enunciado:
- `RecursiveCharacterTextSplitter` com `separators=["\n\n", "\n", ". ", " ", ""]`
- `chunk_overlap` = 10–15% do `chunk_size`
- **Comparar ≥2 configurações de `chunk_size`** (a demo da Aula 07 usa 256,
  512 e 1024 — escolher 2 dessas 3, ex: 512 vs 1024)
- `OllamaEmbeddings(model='nomic-embed-text')` — **único** modelo de
  embedding aceito (nada de OpenAI/pago)
- `gemma4:cloud` exclusivo para geração, `temperature=0`
- `ChromaDB` local (`chromadb.Client()` ou `PersistentClient()`), coleção
  nomeada pelo domínio (ex: `educacao_financeira`)
- A resposta final **cita o chunk/documento de origem**
- Função central `buscar(consulta)` clara e modular — **será reaproveitada
  como tool no CKP03**, então não deixar a lógica espalhada/acoplada à UI

---

## 3. RAGAS — faithfulness + answer_relevancy (obrigatório, 3,0 pts)

- **≥5 perguntas de teste**, rodadas para **cada uma das 2 configurações de
  chunking** → mínimo 10 execuções completas do pipeline
- Métricas: `faithfulness` (a resposta está fundamentada nos documentos
  recuperados?) e `answer_relevancy` (a resposta responde à pergunta?)
- Meta: faithfulness médio **≥ 0,7** (zona ideal ≥ 0,9). **Abaixo de 0,5 é
  sinal de alucinação significativa — iterar no chunking antes de entregar.**
- Montar uma tabela final: pergunta × faithfulness × answer_relevancy, para
  cada config de chunk_size, e **justificar por escrito qual configuração
  ganhou e por quê** (não basta rodar o número, a rubrica pede comparação
  justificada pelos dados) — essa tabela vai no `README.md` (seção
  "Comparação de chunking")

**Pegadinha técnica:** a lib `ragas` por padrão tenta usar OpenAI como juiz
e para embeddings internos. Como só é permitido usar o stack Ollama, é
preciso envolver explicitamente o `ChatOllama` (`gemma4:cloud`) e o
`OllamaEmbeddings` (`nomic-embed-text`) com os wrappers do RAGAS:

```python
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

ragas_llm = LangchainLLMWrapper(chat_ollama_gemma4)
ragas_embeddings = LangchainEmbeddingsWrapper(ollama_embeddings_nomic)
```
Sem isso, o `ragas.evaluate()` vai tentar chamar a API da OpenAI e falhar
(ou pior, usar uma chave de outra conta sem querer).

---

## 4. Diferenciais (até +1,0, nota limitada a 10,0)

Com 3 diferenciais de 0,5 cada (soma 1,5) mas teto de +1,0 — fazer **2 dos
3** já maximiza a nota sem esforço extra desnecessário. Sugestão de
prioridade:

1. **Metadata filtering (+0,5)** — mais fácil de implementar: ao indexar,
   guardar metadata por chunk (`fonte`, `orgao`, `categoria` — ex:
   `orcamento`, `divida`, `investimento`). Demonstrar uma busca com
   `where={"categoria": "divida"}` e mostrar que filtra corretamente.
2. **Reranking (+0,5)** — usar `cross-encoder/ms-marco-MiniLM-L-6-v2` (roda
   local via `sentence-transformers`, não precisa de API paga) pra reordenar
   os top-k do ChromaDB antes de mandar pro LLM. Bom ganho de qualidade,
   fácil de medir (comparar faithfulness com/sem reranking).
3. **Interface Gradio (+0,5)** — se sobrar tempo. `gr.ChatInterface` com a
   fonte citada na resposta — dá pra reaproveitar o tema já feito no CKP01
   (`app/theme.py` daquele projeto) e rodar local como no CKP01
   (`python -m app.main`, `http://localhost:7860`).

---

## 5. Checklist mapeado à rubrica (10,0 pontos)

### 5.1 Pipeline RAG funcional — 3,5 pts
- [ ] `load`: carregar os 5 PDFs (ex: `PyPDFLoader` ou `UnstructuredPDFLoader`)
- [ ] `split`: `RecursiveCharacterTextSplitter` com os separators certos
- [ ] `embed`: `OllamaEmbeddings(model='nomic-embed-text')`
- [ ] `store`: `ChromaDB` persistente, coleção nomeada pelo domínio
- [ ] `retrieve`: função `buscar(consulta)` retornando top-k chunks relevantes
- [ ] `generate`: `gemma4:cloud`, `temperature=0`, resposta cita a fonte
- [ ] Testar manualmente 5 perguntas reais do domínio e conferir se recupera
      documento certo e cita a fonte

### 5.2 Comparação de chunking + RAGAS — 3,0 pts
- [ ] 2 configurações de `chunk_size` (ex: 512 e 1024), overlap 10-15%
- [ ] RAGAS `faithfulness` + `answer_relevancy` em ≥5 perguntas por config
- [ ] Tabela comparativa no `README.md`
- [ ] Conclusão por escrito: qual config ganhou, com base nos números

### 5.3 Qualidade da base de conhecimento — 2,0 pts
- [ ] 5 documentos reais (tabela da seção 1), com link de origem citado
- [ ] Confirmar que os links ainda funcionam antes de entregar
- [ ] Base rica o bastante pra responder pergunta não-trivial (ex: "qual a
      diferença entre Tesouro Selic e Tesouro IPCA+?", não só definição simples)

### 5.4 Código e documentação — 1,5 pts
- [ ] Funções modulares (`carregar_documentos`, `dividir_chunks`,
      `indexar`, `buscar`, `gerar_resposta`), cada uma no seu módulo
      (ver estrutura da seção 2) — nada de script monolítico
- [ ] Comentários em PT-BR só onde agregam
- [ ] `README.md` com nomes/RMs de todos os integrantes (reaproveitar a
      tabela do CKP01) + **instruções de como adicionar novos documentos à
      base** (passo a passo: onde colocar o PDF em `docs/`, qual comando
      rodar para reindexar)

---

## 6. Cronograma (alinhado às aulas)

| Quando | Entregável interno |
|---|---|
| Aula 05 | Documentos carregados, 1 configuração de splitter funcionando, 1 busca semântica retornando resultado (check-in com o professor) |
| Aula 06 | Pipeline completo retrieve → generate rodando; começar comparação de chunking e gerar as primeiras métricas RAGAS |
| Aula 06→07 | Fechar as 2 configs de chunking com RAGAS completo; decidir quais 2 diferenciais fazer |
| Aula 07 | Apresentação do professor (sem apresentação do grupo) — início da janela de 1 semana |
| Antes da Aula 08 | Testar em ambiente limpo (clone novo + venv novo), revisar README, montar o `.zip` |
| Aula 08, até 23:59 | **Entrega via Teams** (só o líder envia): `.zip` do projeto (`app/`, `docs/`, `.env.example`, `requirements.txt`, `README.md`) |

---

## 7. Armadilhas comuns (evitar)

- Usar outro embedding que não `nomic-embed-text` (ex: OpenAI) — zera o
  requisito, mesmo que funcione tecnicamente
- RAGAS chamando OpenAI por padrão em vez do Ollama (ver seção 3)
- Comparar chunking só "no olho" sem números do RAGAS — a rubrica pede
  comparação quantitativa
- Esquecer de citar a fonte na resposta final do RAG
- Entregar sem testar em ambiente limpo (clone novo + venv novo) antes —
  pode faltar algo no `requirements.txt` ou um caminho hardcoded que só
  funciona na máquina de quem desenvolveu
- Incluir o `.env` (com a chave real) no `.zip` — igual ao CKP01, só o
  `.env.example` vai junto
- Esquecer o `chroma_db/` gerado fora do `.zip` (ou incluir ele por engano
  junto com lixo de cache — ver seção "o que entra no zip" do plano em etapas)
- Faithfulness baixo (<0,5) e entregar assim mesmo — é sinal de que o
  chunking ou o prompt de geração precisam de ajuste, não algo pra ignorar

---

## 8. Antes de enviar — checklist final

- [ ] `python -m app.main` (ou equivalente) sobe sem erro num ambiente limpo
- [ ] Os 5 documentos reais estão em `docs/` e citados no README
- [ ] `README.md` com nomes + RMs de todos os integrantes + instruções de
      como adicionar documento novo
- [ ] Faithfulness médio ≥ 0,7 documentado, com a tabela comparativa
- [ ] `.env` **não** está no `.zip` (só `.env.example`)
- [ ] Líder do grupo envia via Teams, na tarefa do professor, até 23:59 do
      dia da Aula 08

Ver o [plano em etapas](PLANO_ACAO_CKP02_ETAPAS.md) para o passo a passo
detalhado de execução.
