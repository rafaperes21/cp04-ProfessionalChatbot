"""Reranking dos resultados da busca com um cross-encoder local (diferencial +0,5).

Não usa API paga — o modelo roda localmente via sentence-transformers.
"""

from sentence_transformers import CrossEncoder

_MODELO = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_reranker: CrossEncoder | None = None


def _get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(_MODELO)
    return _reranker


def rerank(consulta: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    """Reordena os chunks por relevância real à consulta (cross-encoder).

    A busca vetorial do ChromaDB usa similaridade de embeddings, que é
    rápida mas aproximada; o cross-encoder lê consulta+chunk juntos e dá um
    score de relevância mais preciso, ao custo de ser mais lento — por isso
    rerankeamos só os top-N já pré-filtrados pela busca vetorial, não a
    base inteira.
    """
    if not chunks:
        return chunks
    reranker = _get_reranker()
    pares = [(consulta, c["texto"]) for c in chunks]
    scores = reranker.predict(pares)
    chunks_com_score = [
        {**c, "score_rerank": float(score)} for c, score in zip(chunks, scores)
    ]
    chunks_ordenados = sorted(
        chunks_com_score, key=lambda c: c["score_rerank"], reverse=True
    )
    return chunks_ordenados[:top_k]
