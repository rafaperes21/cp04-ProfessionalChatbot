"""Testes do splitter — offline, sem chamar nenhum modelo."""

from langchain_core.documents import Document

from app.chunking import CONFIGS_CHUNKING, dividir_chunks


def _documento_grande(n_paragrafos: int = 50) -> list[Document]:
    paragrafo = (
        "Educação financeira pessoal envolve organizar orçamento, planejar "
        "metas de economia e entender conceitos de investimento de forma "
        "responsável. "
    ) * 3
    texto = "\n\n".join(paragrafo for _ in range(n_paragrafos))
    return [Document(page_content=texto, metadata={"fonte": "doc_teste"})]


def test_configs_chunking_tem_duas_opcoes():
    assert len(CONFIGS_CHUNKING) >= 2


def test_overlap_esta_na_faixa_de_10_a_15_por_cento():
    for nome, config in CONFIGS_CHUNKING.items():
        razao = config["chunk_overlap"] / config["chunk_size"]
        assert 0.10 <= razao <= 0.15, f"{nome}: overlap fora da faixa 10-15%"


def test_config_menor_gera_mais_chunks_que_a_maior():
    documentos = _documento_grande()
    nomes = list(CONFIGS_CHUNKING)
    tamanhos = [CONFIGS_CHUNKING[n]["chunk_size"] for n in nomes]
    nome_menor = nomes[tamanhos.index(min(tamanhos))]
    nome_maior = nomes[tamanhos.index(max(tamanhos))]

    chunks_menor = dividir_chunks(documentos, nome_menor)
    chunks_maior = dividir_chunks(documentos, nome_maior)

    assert len(chunks_menor) > len(chunks_maior)


def test_chunks_preservam_metadata_da_fonte():
    documentos = _documento_grande()
    chunks = dividir_chunks(documentos, next(iter(CONFIGS_CHUNKING)))
    assert all(c.metadata.get("fonte") == "doc_teste" for c in chunks)


def test_chunks_respeitam_tamanho_maximo_aproximado():
    documentos = _documento_grande()
    for nome, config in CONFIGS_CHUNKING.items():
        chunks = dividir_chunks(documentos, nome)
        # RecursiveCharacterTextSplitter pode passar um pouco do limite em
        # trechos sem separador — toleramos uma margem de 20%.
        limite = config["chunk_size"] * 1.2
        estouros = [len(c.page_content) for c in chunks if len(c.page_content) > limite]
        assert not estouros, f"{nome}: chunks estourando o limite: {estouros}"
