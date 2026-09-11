"""Fixtures e utilitarios compartilhados pelos testes.

`FakeListChatModel` puro depende do pacote `transformers` para contar tokens
(usa um tokenizer GPT-2 como fallback). Para nao adicionar essa dependencia
pesada so para os testes, usamos uma contagem simples por palavras.
"""

from langchain_core.language_models.fake_chat_models import FakeListChatModel


class FakeChatModel(FakeListChatModel):
    """FakeListChatModel com contagem de tokens leve (sem `transformers`)."""

    def get_num_tokens(self, text: str) -> int:
        return len(text.split())
