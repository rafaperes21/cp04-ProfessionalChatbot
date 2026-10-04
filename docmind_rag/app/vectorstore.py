"""Gera embeddings com nomic-embed-text e indexa no ChromaDB local."""

import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

load_dotenv()

CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"


def build_embeddings() -> OllamaEmbeddings:
    if not os.getenv("OLLAMA_API_KEY"):
        raise RuntimeError(
            "OLLAMA_API_KEY não encontrada. Copie .env.example para .env e "
            "preencha com sua chave da Ollama Cloud."
        )
    return OllamaEmbeddings(model="nomic-embed-text")


def indexar(
    chunks: list[Document], nome_colecao: str, embeddings: OllamaEmbeddings
) -> chromadb.Collection:
    """Cria (ou recria do zero) uma coleção ChromaDB com os chunks dados."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(nome_colecao)
    except Exception:
        pass
    colecao = client.create_collection(nome_colecao)

    textos = [c.page_content for c in chunks]
    metadados = [c.metadata for c in chunks]
    ids = [f"{nome_colecao}_{i}" for i in range(len(chunks))]

    # embed_documents em lotes — evita mandar milhares de textos numa única
    # chamada (timeout/payload grande) e dá feedback de progresso.
    TAMANHO_LOTE = 64
    for inicio in range(0, len(textos), TAMANHO_LOTE):
        fim = inicio + TAMANHO_LOTE
        vetores_lote = embeddings.embed_documents(textos[inicio:fim])
        colecao.add(
            ids=ids[inicio:fim],
            embeddings=vetores_lote,
            documents=textos[inicio:fim],
            metadatas=metadados[inicio:fim],
        )

    return colecao


def get_collection(nome_colecao: str) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_collection(nome_colecao)
