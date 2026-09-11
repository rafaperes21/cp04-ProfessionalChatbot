"""Estratégias de memória gerenciada para o chatbot.

Implementa as 3 estratégias vistas em aula (Buffer, Summary, TokenBuffer) e
expõe qual delas é usada pelo chatbot em produção via `build_memory`.

Justificativa da escolha (TokenBuffer, ~1200 tokens):
No domínio de atendimento ao cliente, detalhes exatos citados pelo usuário
(número de pedido, nome de produto, prazo combinado) não podem ser parafraseados
por um resumo automático — um erro de paráfrase pode levar a uma ação errada
(ex: trocar o produto errado). O ConversationTokenBufferMemory mantém os turnos
recentes literalmente, e descarta os mais antigos ao ultrapassar o limite de
tokens, o que garante: (1) fidelidade aos dados citados recentemente, e (2) um
teto previsível de custo por chamada ao modelo, diferente do BufferMemory puro
(que cresce sem limite) e do SummaryMemory puro (que resume tudo, inclusive
detalhes recentes que ainda importam).
"""

from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationTokenBufferMemory,
)

MEMORY_STRATEGY = "token_buffer"
TOKEN_BUFFER_LIMIT = 1200


def get_buffer_memory():
    """Memória de buffer simples — guarda o histórico completo da conversa."""
    return ConversationBufferMemory(memory_key="history", return_messages=True)


def get_summary_memory(llm):
    """Memória de resumo — reescreve o histórico como um resumo contínuo."""
    return ConversationSummaryMemory(
        llm=llm, memory_key="history", return_messages=True
    )


def get_token_buffer_memory(llm, max_token_limit: int = TOKEN_BUFFER_LIMIT):
    """Memória com janela de tokens — mantém os turnos recentes até o limite."""
    return ConversationTokenBufferMemory(
        llm=llm,
        max_token_limit=max_token_limit,
        memory_key="history",
        return_messages=True,
    )


def build_memory(llm):
    """Estratégia usada pelo chatbot em produção (ver justificativa acima)."""
    return get_token_buffer_memory(llm)
