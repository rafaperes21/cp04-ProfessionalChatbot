"""Entry point do chatbot: interface Gradio ligando as 2 chains.

Rodar com: `python -m app.main` (abre em http://localhost:7860)
"""

import gradio as gr

from app.chain import build_analise_chain, build_conversation_chain
from app.theme import FIN_CSS, FIN_THEME

ICON_PATH = "app/assets/icon.png"

conversation_chain = build_conversation_chain()
analise_chain = build_analise_chain()


def responder(mensagem: str, history: list):
    resposta = conversation_chain.predict(input=mensagem)

    try:
        analise = analise_chain.invoke({"input": mensagem})
        analise_texto = analise.model_dump_json(indent=2)
    except Exception as exc:  # saída fora do formato esperado, por ex.
        analise_texto = f"(falha ao estruturar a análise: {exc})"

    return resposta, analise_texto


with gr.Blocks(title="FinComigo — Educação Financeira") as demo:
    gr.Markdown(
        '<h2 id="fincomigo-header">FinComigo</h2>'
        '<span id="fincomigo-badge">Educação Financeira · CKP01</span>'
    )

    analise_saida = gr.Textbox(
        label="Análise estruturada (AnaliseConsulta)",
        lines=16,
        interactive=False,
        render=False,
    )

    with gr.Row():
        with gr.Column(scale=2):
            gr.ChatInterface(
                fn=responder,
                additional_outputs=[analise_saida],
                chatbot=gr.Chatbot(
                    label="Conversa com a Fê",
                    avatar_images=(None, ICON_PATH),
                    height=480,
                ),
                examples=[
                    "Quero economizar R$500 por mês, por onde eu começo?",
                    "O que é Tesouro Direto?",
                    "Estou com dívida no cartão de crédito, o que eu faço?",
                ],
            )
        with gr.Column(scale=1):
            analise_saida.render()


if __name__ == "__main__":
    demo.launch(theme=FIN_THEME, css=FIN_CSS, favicon_path=ICON_PATH)
