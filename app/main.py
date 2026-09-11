"""Entry point do chatbot: interface Gradio ligando as 2 chains.

Rodar com: `python -m app.main` (abre em http://localhost:7860)
"""

import gradio as gr

from app.chain import build_analise_chain, build_conversation_chain
from app.theme import FIN_CSS, FIN_THEME

conversation_chain = build_conversation_chain()
analise_chain = build_analise_chain()


def responder(mensagem: str, historico_ui: list):
    resposta = conversation_chain.predict(input=mensagem)

    try:
        analise = analise_chain.invoke({"input": mensagem})
        analise_texto = analise.model_dump_json(indent=2)
    except Exception as exc:  # saída fora do formato esperado, por ex.
        analise_texto = f"(falha ao estruturar a análise: {exc})"

    historico_ui = historico_ui + [
        {"role": "user", "content": mensagem},
        {"role": "assistant", "content": resposta},
    ]
    return historico_ui, analise_texto, ""


with gr.Blocks(title="FinComigo — Educação Financeira") as demo:
    gr.Markdown(
        '<h2 id="fincomigo-header">FinComigo</h2>'
        '<span id="fincomigo-badge">Educação Financeira · CKP01</span>'
    )

    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Conversa com a Fê")
            with gr.Row():
                entrada = gr.Textbox(
                    label="Sua mensagem",
                    placeholder="Digite e pressione Enter...",
                    scale=4,
                )
                enviar = gr.Button("Enviar", variant="primary", scale=1)
        with gr.Column(scale=1):
            analise_saida = gr.Textbox(
                label="Análise estruturada (AnaliseConsulta)",
                lines=12,
                interactive=False,
            )

    entrada.submit(
        responder,
        inputs=[entrada, chatbot],
        outputs=[chatbot, analise_saida, entrada],
    )
    enviar.click(
        responder,
        inputs=[entrada, chatbot],
        outputs=[chatbot, analise_saida, entrada],
    )


if __name__ == "__main__":
    demo.launch(theme=FIN_THEME, css=FIN_CSS)
