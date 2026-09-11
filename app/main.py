"""Entry point do chatbot: interface Gradio ligando as 2 chains.

Rodar com: `python -m app.main` (abre em http://localhost:7860)
"""

import gradio as gr

from app.chain import build_analise_chain, build_conversation_chain

conversation_chain = build_conversation_chain()
analise_chain = build_analise_chain()


def responder(mensagem: str, historico_ui: list):
    resposta = conversation_chain.predict(input=mensagem)

    try:
        analise = analise_chain.invoke({"input": mensagem})
        analise_texto = analise.model_dump_json(indent=2)
    except Exception as exc:  # saída fora do formato esperado, por ex.
        analise_texto = f"(falha ao estruturar a análise: {exc})"

    historico_ui.append((mensagem, resposta))
    return historico_ui, analise_texto, ""


with gr.Blocks(title="FinComigo — Educação Financeira") as demo:
    gr.Markdown("## FinComigo — Assistente de Educação Financeira (CKP01)")

    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Conversa com a Fê")
            entrada = gr.Textbox(
                label="Sua mensagem", placeholder="Digite e pressione Enter..."
            )
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


if __name__ == "__main__":
    demo.launch()
