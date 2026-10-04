# CKP02 DocMind RAG — Plano em Etapas (execução passo a passo)

Detalhamento técnico do [PLANO_ACAO_CKP02.md](PLANO_ACAO_CKP02.md) (visão
geral/rubrica). Aqui cada etapa tem o que fazer, o código-base pra começar e
como verificar que funcionou antes de ir pra próxima. Pensado pra ser
seguido em ordem, uma etapa de cada vez.

**Onde isso mora:** pasta nova `docmind_rag/` na raiz do repo
(`cp04-ProfessionalChatbot`), separada do `app/` do CKP01 — mesmo repo,
mesmo grupo, domínio contínuo, mas entregável independente.

---

## Etapa 0 — Estrutura e ambiente (15 min)

```bash
mkdir -p docmind_rag/{app,docs,tests}
cd docmind_rag
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
```

Criar `requirements.txt`:
```
langchain>=1.0.0
langchain-ollama>=1.0.0
langchain-community>=0.3.0
langchain-text-splitters>=1.0.0
chromadb>=0.5.0
pypdf>=5.0.0
ragas>=0.2.0
datasets>=3.0.0
sentence-transformers>=3.0.0
python-dotenv>=1.0.0
gradio>=4.0.0
pytest>=8.0.0
```
(`sentence-transformers` é só pro diferencial de reranking — pode tirar se
decidirem não fazer esse diferencial.)

```bash
.venv/bin/pip install -r requirements.txt
cp ../.env.example .env   # reaproveita o padrão do CKP01: OLLAMA_API_KEY=
```

**Verificação:** `.venv/bin/python -c "import langchain, chromadb, ragas; print('ok')"` sem erro.

---

## Etapa 1 — Baixar os 5 documentos reais (20 min)

Baixar os PDFs da tabela do plano geral para `docs/`, com nome de arquivo
descritivo (vai facilitar o metadata filtering depois):

```bash
cd docs
curl -L -o bcb_caderno_educacao_financeira.pdf "https://www.bcb.gov.br/content/cidadaniafinanceira/documentos_cidadania/Cuidando_do_seu_dinheiro_Gestao_de_Financas_Pessoais/caderno_cidadania_financeira.pdf"
curl -L -o cvm_guia_planejamento_financeiro.pdf "https://www.gov.br/investidor/pt-br/educacional/publicacoes-educacionais/guias/guia-de-planejamento-financeiro/guia-planejamento-financeiro.pdf"
curl -L -o enap_guia_investidor_tesouro.pdf "https://repositorio.enap.gov.br/bitstream/1/6248/1/Guia_Investidor%20TD.pdf"
curl -L -o febraban_guia_educacao_financeira.pdf "https://cmsarquivos.febraban.org.br/Arquivos/documentos/PDF/febraban-guia%20de%20boas%20pr%C3%A1ticas-v7-web.pdf"
curl -L -o b3_regulamento_tesouro_direto.pdf "https://www.b3.com.br/data/files/1B/D6/29/4F/22EC46101305DC46AC094EA8/Regulamento_Tesouro_Direto.pdf"
cd ..
```

**Verificação:** `file docs/*.pdf` — todos devem aparecer como `PDF document`,
não HTML (um link quebrado geralmente baixa uma página de erro em HTML em
vez do PDF, ou redireciona para um PDF de aviso de 1 página — foi o que
aconteceu com 2 das 5 URLs originais do enunciado; ver `docs/FONTES.md` para
as correções já aplicadas). Abrir cada um e conferir que o conteúdo bate com
a tabela do plano geral.

Criar `docs/FONTES.md` com a tabela de proveniência (documento → URL → órgão
→ data de acesso) — vira a base da seção "fontes citadas" do README depois.

---

## Etapa 2 — `document_loader.py` (load) — 20 min

```python
# app/document_loader.py
"""Carrega os PDFs da base de conhecimento (pasta docs/)."""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

DOCS_DIR = Path(__file__).parent.parent / "docs"


def carregar_documentos(docs_dir: Path = DOCS_DIR) -> list:
    """Carrega todos os PDFs de docs_dir, um Document por página."""
    documentos = []
    for pdf_path in sorted(docs_dir.glob("*.pdf")):
        loader = PyPDFLoader(str(pdf_path))
        paginas = loader.load()
        for pagina in paginas:
            pagina.metadata["fonte"] = pdf_path.stem
        documentos.extend(paginas)
    return documentos
```

**Verificação:**
```bash
.venv/bin/python -c "
from app.document_loader import carregar_documentos
docs = carregar_documentos()
print(f'{len(docs)} páginas carregadas de {len(set(d.metadata[\"fonte\"] for d in docs))} documentos')
print(docs[0].page_content[:200])
"
```
Deve mostrar um número de páginas plausível (dezenas a centenas, dado que um
dos PDFs tem quase 100 páginas) e o texto do começo do primeiro documento legível
(não lixo binário — sinal de PDF mal extraído).

---

## Etapa 3 — `chunking.py` (split, 2 configurações) — 20 min

```python
# app/chunking.py
"""Divide os documentos em chunks — 2 configurações comparáveis (Aula 06)."""

from langchain_text_splitters import RecursiveCharacterTextSplitter

SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

CONFIGS_CHUNKING = {
    "pequeno_512": {"chunk_size": 512, "chunk_overlap": 64},   # ~12,5% overlap
    "grande_1024": {"chunk_size": 1024, "chunk_overlap": 128},  # ~12,5% overlap
}


def dividir_chunks(documentos: list, config_nome: str) -> list:
    config = CONFIGS_CHUNKING[config_nome]
    splitter = RecursiveCharacterTextSplitter(
        separators=SEPARATORS,
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
    )
    return splitter.split_documents(documentos)
```

**Verificação:** rodar para as 2 configs e comparar a quantidade de chunks
gerados (config menor deve gerar mais chunks que a maior):
```bash
.venv/bin/python -c "
from app.document_loader import carregar_documentos
from app.chunking import dividir_chunks
docs = carregar_documentos()
for nome in ['pequeno_512', 'grande_1024']:
    chunks = dividir_chunks(docs, nome)
    print(f'{nome}: {len(chunks)} chunks')
"
```

---

## Etapa 4 — `vectorstore.py` (embed + store) — 30 min

```python
# app/vectorstore.py
"""Gera embeddings com nomic-embed-text e indexa no ChromaDB local."""

import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings

load_dotenv()

CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"


def build_embeddings() -> OllamaEmbeddings:
    if not os.getenv("OLLAMA_API_KEY"):
        raise RuntimeError("OLLAMA_API_KEY não encontrada no .env")
    return OllamaEmbeddings(model="nomic-embed-text")


def indexar(chunks: list, nome_colecao: str, embeddings: OllamaEmbeddings) -> chromadb.Collection:
    """Cria/sobrescreve uma coleção ChromaDB com os chunks dados."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(nome_colecao)
    except Exception:
        pass
    colecao = client.create_collection(nome_colecao)

    textos = [c.page_content for c in chunks]
    vetores = embeddings.embed_documents(textos)
    metadados = [c.metadata for c in chunks]
    ids = [f"{nome_colecao}_{i}" for i in range(len(chunks))]

    colecao.add(ids=ids, embeddings=vetores, documents=textos, metadatas=metadados)
    return colecao
```

**Nota de custo/tempo:** `embed_documents` faz 1 chamada real por chunk (ou
em lote, dependendo da versão) à Ollama Cloud — com ~1024 chunks isso pode
levar alguns minutos. Rodar uma vez por configuração de chunking e
persistir (`PersistentClient`) pra não reindexar toda hora durante o
desenvolvimento.

**Verificação:**
```bash
.venv/bin/python -c "
from app.document_loader import carregar_documentos
from app.chunking import dividir_chunks
from app.vectorstore import build_embeddings, indexar
docs = carregar_documentos()
chunks = dividir_chunks(docs, 'pequeno_512')
emb = build_embeddings()
colecao = indexar(chunks, 'educacao_financeira_512', emb)
print(colecao.count(), 'chunks indexados')
"
```

---

## Etapa 5 — `retrieval.py` (retrieve — a função `buscar`) — 20 min

Esta é a função que **vira tool no CKP03** — manter a assinatura limpa.

```python
# app/retrieval.py
"""Busca semântica na coleção ChromaDB — função buscar(consulta), reaproveitada no CKP03."""

import chromadb

from app.vectorstore import CHROMA_DIR, build_embeddings


def buscar(consulta: str, nome_colecao: str, top_k: int = 4, where: dict | None = None) -> list[dict]:
    """Retorna os top_k chunks mais relevantes para a consulta.

    where: filtro de metadata opcional (diferencial de metadata filtering),
    ex: {"fonte": "b3_regulamento_tesouro_direto"}.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    colecao = client.get_collection(nome_colecao)
    embeddings = build_embeddings()

    vetor_consulta = embeddings.embed_query(consulta)
    resultado = colecao.query(
        query_embeddings=[vetor_consulta],
        n_results=top_k,
        where=where,
    )

    return [
        {"texto": doc, "metadata": meta, "distancia": dist}
        for doc, meta, dist in zip(
            resultado["documents"][0], resultado["metadatas"][0], resultado["distances"][0]
        )
    ]
```

**Verificação:** buscar algo que sabidamente está nos documentos (ex: "o que
é Tesouro Selic?") e conferir que o chunk retornado realmente fala sobre
isso, com `metadata["fonte"]` apontando pro PDF certo.

---

## Etapa 6 — `generation.py` (generate, com citação de fonte) — 20 min

```python
# app/generation.py
"""Geração da resposta final com gemma4:cloud, citando a fonte."""

import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

load_dotenv()

SYSTEM_PROMPT = """\
Você é um assistente de educação financeira que responde SOMENTE com base
nos trechos de documentos fornecidos abaixo. Se a resposta não estiver nos
trechos, diga que não encontrou essa informação na base — não invente.

Ao final da resposta, cite a fonte entre colchetes, ex: [Fonte: nome_do_documento].

Trechos disponíveis:
{contexto}
"""


def build_llm() -> ChatOllama:
    if not os.getenv("OLLAMA_API_KEY"):
        raise RuntimeError("OLLAMA_API_KEY não encontrada no .env")
    return ChatOllama(model="gemma4:cloud", temperature=0)


def gerar_resposta(pergunta: str, chunks_relevantes: list[dict]) -> str:
    contexto = "\n\n".join(
        f"[{c['metadata']['fonte']}] {c['texto']}" for c in chunks_relevantes
    )
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "{pergunta}")]
    )
    chain = prompt | build_llm()
    resposta = chain.invoke({"contexto": contexto, "pergunta": pergunta})
    return resposta.content
```

---

## Etapa 7 — `rag_pipeline.py` (junta tudo) — 15 min

```python
# app/rag_pipeline.py
"""Pipeline RAG completo: load (já rodado na indexação) → retrieve → generate."""

from app.generation import gerar_resposta
from app.retrieval import buscar


def responder(pergunta: str, nome_colecao: str, top_k: int = 4) -> dict:
    chunks = buscar(pergunta, nome_colecao, top_k=top_k)
    resposta = gerar_resposta(pergunta, chunks)
    return {"pergunta": pergunta, "resposta": resposta, "chunks_usados": chunks}
```

**Verificação manual (checkpoint da Aula 06):** rodar 5 perguntas reais do
domínio contra a coleção já indexada e ler as respostas:

```python
perguntas_teste = [
    "O que é Tesouro Selic?",
    "Como faço um orçamento mensal?",
    "Quais são os passos para sair de uma dívida de cartão de crédito?",
    "O que é reserva de emergência e quanto ela deveria ter?",
    "Qual a diferença entre Tesouro Selic e Tesouro IPCA+?",
]
```
Para cada uma, conferir: recuperou chunk relevante? A resposta cita a fonte?
A resposta é fiel ao conteúdo do documento (não inventada)?

---

## Etapa 8 — `ragas_eval.py` (avaliação RAGAS) — 40 min

**Atenção à pegadinha do RAGAS com OpenAI** — ver seção 3 do plano geral.

```python
# app/ragas_eval.py
"""Avaliação RAGAS: faithfulness + answer_relevancy, por configuração de chunking."""

from datasets import Dataset
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import answer_relevancy, faithfulness

from app.generation import build_llm
from app.rag_pipeline import responder
from app.vectorstore import build_embeddings

PERGUNTAS_TESTE = [
    "O que é Tesouro Selic?",
    "Como faço um orçamento mensal?",
    "Quais são os passos para sair de uma dívida de cartão de crédito?",
    "O que é reserva de emergência e quanto ela deveria ter?",
    "Qual a diferença entre Tesouro Selic e Tesouro IPCA+?",
]


def avaliar_configuracao(nome_colecao: str) -> dict:
    perguntas, respostas, contextos = [], [], []
    for pergunta in PERGUNTAS_TESTE:
        resultado = responder(pergunta, nome_colecao)
        perguntas.append(pergunta)
        respostas.append(resultado["resposta"])
        contextos.append([c["texto"] for c in resultado["chunks_usados"]])

    dataset = Dataset.from_dict(
        {"question": perguntas, "answer": respostas, "contexts": contextos}
    )

    ragas_llm = LangchainLLMWrapper(build_llm())
    ragas_embeddings = LangchainEmbeddingsWrapper(build_embeddings())

    resultado = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=ragas_llm,
        embeddings=ragas_embeddings,
    )
    return resultado.to_pandas()


if __name__ == "__main__":
    for nome in ["educacao_financeira_512", "educacao_financeira_1024"]:
        print(f"=== {nome} ===")
        df = avaliar_configuracao(nome)
        print(df[["question", "faithfulness", "answer_relevancy"]])
        print(f"Faithfulness médio: {df['faithfulness'].mean():.2f}")
        print(f"Answer relevancy médio: {df['answer_relevancy'].mean():.2f}\n")
```

**Verificação:** rodar e conferir que os números saem entre 0 e 1 (não erro
de autenticação OpenAI — se aparecer erro de API key da OpenAI, é sinal de
que os wrappers não foram passados certo pro `evaluate()`). Se faithfulness
médio < 0,7, ver passo 8.1 abaixo antes de seguir.

### 8.1 — Se faithfulness vier baixo (<0,7)

Por ordem de esforço crescente:
1. Revisar o `SYSTEM_PROMPT` de geração — reforçar "responda SOMENTE com
   base no contexto, nunca invente"
2. Aumentar `top_k` na busca (mais contexto disponível pra fundamentar)
3. Trocar a config de chunking (chunks muito pequenos podem cortar uma
   explicação no meio; muito grandes podem diluir o trecho relevante com
   ruído)
4. Conferir se a extração do PDF não está corrompida (texto quebrado/colado
   sem espaço prejudica tanto o embedding quanto a geração)

---

## Etapa 9 — Montar a tabela comparativa e decidir o vencedor — 15 min

No `README.md`, seção "Comparação de chunking":

| Config | chunk_size | overlap | Faithfulness médio | Answer relevancy médio | Nº chunks indexados |
|---|---|---|---|---|---|
| pequeno_512 | 512 | 64 | _preencher_ | _preencher_ | _preencher_ |
| grande_1024 | 1024 | 128 | _preencher_ | _preencher_ | _preencher_ |

Escrever 2-3 frases explicando **por que** uma ganhou (ex: "chunks menores
tiveram faithfulness mais alto porque preservam passagens mais específicas,
evitando diluir a resposta com conteúdo de outras seções do mesmo PDF").

---

## Etapa 10 — Diferenciais (opcional, priorizar 2 de 3 — até +1,0)

### 10.1 Metadata filtering (+0,5) — 20 min
Já dá de graça pelo `where=` em `buscar()` (Etapa 5). Só precisa demonstrar
no README com um exemplo real: buscar algo filtrando por
`where={"fonte": "b3_regulamento_tesouro_direto"}` e mostrar que só retorna
chunks desse documento.

### 10.2 Reranking (+0,5) — 30 min
```python
# dentro de app/retrieval.py, ou um novo app/reranking.py
from sentence_transformers import CrossEncoder

_RERANKER = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(consulta: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    pares = [(consulta, c["texto"]) for c in chunks]
    scores = _RERANKER.predict(pares)
    chunks_ordenados = [c for _, c in sorted(zip(scores, chunks), key=lambda x: -x[0])]
    return chunks_ordenados[:top_k]
```
Buscar mais candidatos do que o necessário (`top_k=10` no `buscar()`) e
deixar o `rerank()` filtrar pros melhores 3-4 antes de mandar pro LLM.
Medir: comparar faithfulness com e sem reranking pra ter um número que
comprove o ganho.

### 10.3 Interface Gradio (+0,5) — 30 min, se sobrar tempo
`app/main.py`, reaproveitando o estilo do `app/main.py` do CKP01
(`gr.ChatInterface`), mas chamando `rag_pipeline.responder()` e mostrando a
fonte citada abaixo da resposta.

---

## Etapa 11 — `README.md` final — 30 min

Seções obrigatórias (reaproveitar a estrutura que funcionou no CKP01):
1. Domínio (igual ao CKP01, FinComigo)
2. Integrantes + RMs (copiar do README do CKP01)
3. Base de conhecimento: tabela dos 5 documentos com fonte/link (de `docs/FONTES.md`)
4. Arquitetura do pipeline (diagrama load→split→embed→store→retrieve→generate)
5. Comparação de chunking + RAGAS (tabela da Etapa 9)
6. Diferenciais implementados, com evidência
7. Como executar (setup, indexação, como rodar uma pergunta)
8. **Como adicionar um documento novo à base** (obrigatório pelo enunciado):
   passo a passo — colocar o PDF em `docs/`, rodar o script de reindexação,
   confirmar que a nova coleção tem mais chunks que antes

---

## Etapa 12 — Teste em ambiente limpo + zip — 20 min

```bash
cd /tmp && git clone <repo> teste-limpo && cd teste-limpo/docmind_rag
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # editar com a chave real
.venv/bin/python -m app.rag_pipeline   # ou o comando de smoke-test que vocês definirem
```

Depois, montar o zip (mesma lógica do CKP01 — conferir antes que o `.env`
real não entra):
```
CKP02_educacao-financeira_grupo.zip
├── app/
├── docs/
├── .env.example
├── requirements.txt
└── README.md
```

(`chroma_db/` **não precisa** ir no zip — o enunciado não pede o índice
pronto, só o código + os documentos + instruções pra reindexar; isso também
mantém o zip pequeno. Deixar isso explícito no README, seção "como
executar".)

---

## Etapa 13 — Entrega

Líder do grupo envia o `.zip` via Teams, na tarefa do professor, até 23:59
do dia da Aula 08. Mesmo fluxo do CKP01.
