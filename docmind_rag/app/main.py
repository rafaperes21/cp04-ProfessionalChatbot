"""Interface Gradio simples para o DocMind RAG (diferencial +0,5).

Rodar com: `python -m app.main` (abre em http://localhost:7860)
"""

import gradio as gr

from app.rag_pipeline import responder

NOME_COLECAO_PADRAO = "educacao_financeira_pequeno_512"  # venceu a comparação RAGAS


def responder_chat(mensagem: str, history: list) -> str:
    resultado = responder(mensagem, NOME_COLECAO_PADRAO, usar_reranking=True)
    fontes = sorted(set(c["metadata"]["fonte"] for c in resultado["chunks_usados"]))
    fontes_texto = ", ".join(fontes)
    return f"{resultado['resposta']}\n\n---\n**Fontes consultadas:** {fontes_texto}"


demo = gr.ChatInterface(
    fn=responder_chat,
    title="DocMind RAG — Educação Financeira Pessoal",
    description=(
        "Pergunte sobre orçamento, dívidas, investimentos (Tesouro Direto) "
        "e planejamento financeiro, com base em documentos oficiais reais "
        "(Banco Central, CVM, Febraban, B3, ENAP)."
    ),
    examples=[
        "O que é Tesouro Selic?",
        "Como faço um orçamento mensal?",
        "Quais os cuidados que devo ter ao usar o cartão de crédito?",
    ],
)


if __name__ == "__main__":
    demo.launch()
