"""Avaliação RAGAS: faithfulness + answer_relevancy, por configuração de chunking.

Importa app._ragas_compat ANTES de qualquer import do pacote `ragas` — ver
o docstring daquele módulo para o porquê (bug conhecido do ragas com uma
dependência do langchain-community que foi removida).
"""

import app._ragas_compat  # noqa: F401 — precisa rodar antes do import do ragas

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
    "Quais os cuidados que devo ter ao usar o cartão de crédito?",
    "O que é reserva de emergência e por que ela é importante?",
    "Qual a diferença entre Tesouro Selic e Tesouro IPCA+?",
]


def avaliar_configuracao(nome_colecao: str, perguntas: list[str] = PERGUNTAS_TESTE):
    """Roda o pipeline RAG para cada pergunta e avalia com RAGAS.

    Esquema de colunas exigido pelo ragas 0.4.x: user_input, response,
    retrieved_contexts (nomes antigos question/answer/contexts foram
    renomeados nas versões recentes da lib).
    """
    perguntas_lista, respostas, contextos = [], [], []
    for pergunta in perguntas:
        resultado = responder(pergunta, nome_colecao)
        perguntas_lista.append(pergunta)
        respostas.append(resultado["resposta"])
        contextos.append([c["texto"] for c in resultado["chunks_usados"]])

    dataset = Dataset.from_dict(
        {
            "user_input": perguntas_lista,
            "response": respostas,
            "retrieved_contexts": contextos,
        }
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
    for nome in ["educacao_financeira_pequeno_512", "educacao_financeira_grande_1024"]:
        print(f"=== {nome} ===")
        df = avaliar_configuracao(nome)
        print(df[["user_input", "faithfulness", "answer_relevancy"]])
        print(f"Faithfulness médio: {df['faithfulness'].mean():.3f}")
        print(f"Answer relevancy médio: {df['answer_relevancy'].mean():.3f}\n")
