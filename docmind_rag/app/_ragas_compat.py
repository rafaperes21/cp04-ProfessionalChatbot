"""Shim de compatibilidade para um bug conhecido do pacote `ragas`.

`ragas/llms/base.py` faz `from langchain_community.chat_models.vertexai import
ChatVertexAI` de forma incondicional (mesmo quem nunca usa Vertex AI é
afetado). Esse submódulo foi removido do `langchain-community` (pacote em
processo de "sunset", ver
https://github.com/langchain-ai/langchain-community/issues/674), então
`import ragas` quebra com `ModuleNotFoundError` em qualquer projeto moderno
que não trave numa versão antiga e incompatível do `langchain-community`.

Este módulo registra um stub em `sys.modules` ANTES do `ragas` ser
importado, satisfazendo o import sem precisar da dependência real do
Google Cloud Vertex AI (que este projeto não usa — só Ollama).

Uso: `import app._ragas_compat` antes de qualquer `import ragas` ou
`from ragas import ...`.
"""

import sys
import types


def _instalar_stub_vertexai() -> None:
    nome_modulo = "langchain_community.chat_models.vertexai"
    if nome_modulo in sys.modules:
        return

    modulo = types.ModuleType(nome_modulo)

    class ChatVertexAI:  # stub — nunca instanciado neste projeto
        def __init__(self, *args, **kwargs):
            raise RuntimeError(
                "ChatVertexAI é um stub de compatibilidade (ragas_compat) — "
                "este projeto usa apenas Ollama, não Vertex AI."
            )

    modulo.ChatVertexAI = ChatVertexAI
    sys.modules[nome_modulo] = modulo


_instalar_stub_vertexai()
