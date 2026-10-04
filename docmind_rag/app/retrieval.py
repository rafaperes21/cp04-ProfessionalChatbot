"""Busca semântica na coleção ChromaDB.

A função `buscar` é o ponto de integração que será reaproveitado como
`@tool` no CKP03 — manter a assinatura simples e estável.
"""

from app.vectorstore import build_embeddings, get_collection


def buscar(
    consulta: str,
    nome_colecao: str,
    top_k: int = 4,
    where: dict | None = None,
) -> list[dict]:
    """Retorna os top_k chunks mais relevantes para a consulta.

    where: filtro de metadata opcional (diferencial de metadata filtering),
    ex: {"fonte": "b3_regulamento_tesouro_direto"}.
    """
    colecao = get_collection(nome_colecao)
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
            resultado["documents"][0],
            resultado["metadatas"][0],
            resultado["distances"][0],
        )
    ]
