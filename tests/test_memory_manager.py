"""Testes das estrategias de memoria (app/memory_manager.py).

Usam um FakeListChatModel no lugar do ChatOllama real, para validar a
mecanica das memorias sem depender de rede/API key.
"""

from langchain_classic.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationTokenBufferMemory,
)
from app.memory_manager import (
    TOKEN_BUFFER_LIMIT,
    build_memory,
    get_buffer_memory,
    get_summary_memory,
    get_token_buffer_memory,
)
from tests.conftest import FakeChatModel


def test_get_buffer_memory_tipo_correto():
    mem = get_buffer_memory()
    assert isinstance(mem, ConversationBufferMemory)


def test_get_summary_memory_tipo_correto():
    fake_llm = FakeChatModel(responses=["resumo da conversa"])
    mem = get_summary_memory(fake_llm)
    assert isinstance(mem, ConversationSummaryMemory)


def test_get_token_buffer_memory_tipo_e_limite():
    fake_llm = FakeChatModel(responses=[])
    mem = get_token_buffer_memory(fake_llm)
    assert isinstance(mem, ConversationTokenBufferMemory)
    assert mem.max_token_limit == TOKEN_BUFFER_LIMIT


def test_build_memory_usa_token_buffer_por_padrao():
    fake_llm = FakeChatModel(responses=[])
    mem = build_memory(fake_llm)
    assert isinstance(mem, ConversationTokenBufferMemory)


def test_token_buffer_retem_turno_mais_recente_apos_5_mais_trocas():
    fake_llm = FakeChatModel(responses=[])
    mem = get_token_buffer_memory(fake_llm, max_token_limit=1200)

    for i in range(6):
        mem.save_context({"input": f"pergunta {i}"}, {"response": f"resposta {i}"})

    historico = mem.load_memory_variables({})["history"]
    assert len(historico) > 0
    assert any("pergunta 5" in m.content for m in historico)


def test_token_buffer_descarta_turnos_antigos_quando_limite_e_pequeno():
    fake_llm = FakeChatModel(responses=[])
    mem = get_token_buffer_memory(fake_llm, max_token_limit=20)

    for i in range(10):
        mem.save_context(
            {"input": f"mensagem numero {i} com bastante texto de enchimento"},
            {"response": f"resposta numero {i} tambem com bastante texto de enchimento"},
        )

    historico = mem.load_memory_variables({})["history"]
    # com limite de tokens pequeno, o primeiro turno nao deve mais estar presente
    assert not any("mensagem numero 0" in m.content for m in historico)
