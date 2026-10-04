"""Divide os documentos em chunks — 2 configurações comparáveis (Aula 06)."""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

# chunk_overlap em ~12,5% do chunk_size (dentro da faixa 10-15% pedida)
CONFIGS_CHUNKING = {
    "pequeno_512": {"chunk_size": 512, "chunk_overlap": 64},
    "grande_1024": {"chunk_size": 1024, "chunk_overlap": 128},
}


def dividir_chunks(documentos: list[Document], config_nome: str) -> list[Document]:
    config = CONFIGS_CHUNKING[config_nome]
    splitter = RecursiveCharacterTextSplitter(
        separators=SEPARATORS,
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
    )
    return splitter.split_documents(documentos)
