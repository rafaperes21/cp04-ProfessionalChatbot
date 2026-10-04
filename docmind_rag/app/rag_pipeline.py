"""Pipeline RAG completo: retrieve → (rerank opcional) → generate
(load/split/embed/store já rodaram na indexação — ver scripts/indexar.py)."""

from app.generation import gerar_resposta
from app.retrieval import buscar


def responder(
    pergunta: str,
    nome_colecao: str,
    top_k: int = 4,
    where: dict | None = None,
    usar_reranking: bool = False,
) -> dict:
    # com reranking, busca mais candidatos (top_k * 3) e deixa o
    # cross-encoder escolher os melhores top_k entre eles
    top_k_busca = top_k * 3 if usar_reranking else top_k
    chunks = buscar(pergunta, nome_colecao, top_k=top_k_busca, where=where)

    if usar_reranking:
        from app.reranking import rerank

        chunks = rerank(pergunta, chunks, top_k=top_k)

    resposta = gerar_resposta(pergunta, chunks)
    return {"pergunta": pergunta, "resposta": resposta, "chunks_usados": chunks}
