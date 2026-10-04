"""Reindexação da base de conhecimento (docs/ -> ChromaDB).

Rodar sempre que um documento novo for adicionado em docs/, ou quando o
código de chunking mudar. Gera as 2 coleções (uma por configuração de
chunking comparada no CKP02).

Uso: python -m scripts.indexar
"""

import time

from app.chunking import CONFIGS_CHUNKING, dividir_chunks
from app.document_loader import carregar_documentos
from app.vectorstore import build_embeddings, indexar


def main() -> None:
    documentos = carregar_documentos()
    fontes = sorted(set(d.metadata["fonte"] for d in documentos))
    print(f"{len(documentos)} páginas carregadas de {len(fontes)} documentos:")
    for fonte in fontes:
        print(f"  - {fonte}")

    embeddings = build_embeddings()

    for nome_config in CONFIGS_CHUNKING:
        chunks = dividir_chunks(documentos, nome_config)
        nome_colecao = f"educacao_financeira_{nome_config}"
        inicio = time.time()
        colecao = indexar(chunks, nome_colecao, embeddings)
        duracao = time.time() - inicio
        print(
            f"{nome_colecao}: {colecao.count()} chunks indexados em {duracao:.1f}s"
        )


if __name__ == "__main__":
    main()
