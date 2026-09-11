"""Testes das 2 chains (app/chain.py) usando um ChatOllama falso.

Nao fazem nenhuma chamada de rede: substituem `app.chain.ChatOllama` por um
FakeListChatModel para validar a fiacao (wiring) do pipeline LCEL, da
ConversationChain com memoria, e do PydanticOutputParser.
"""

import json

import pytest

import app.chain as chain_module
from app.schemas import AnaliseSolicitacao
from tests.conftest import FakeChatModel


def test_build_llm_falha_sem_api_key(monkeypatch):
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        chain_module.build_llm()


def test_build_llm_usa_gemma4_cloud(monkeypatch):
    monkeypatch.setenv("OLLAMA_API_KEY", "chave-de-teste")
    capturado = {}

    class ChatOllamaFalso:
        def __init__(self, model, temperature):
            capturado["model"] = model
            capturado["temperature"] = temperature

    monkeypatch.setattr(chain_module, "ChatOllama", ChatOllamaFalso)

    chain_module.build_llm(temperature=0.7)

    assert capturado["model"] == "gemma4:cloud"
    assert capturado["temperature"] == 0.7


def test_conversation_chain_responde_e_lembra_turnos(monkeypatch):
    monkeypatch.setenv("OLLAMA_API_KEY", "chave-de-teste")
    fake_llm = FakeChatModel(
        responses=["Oi! Sou a Ana, da TechNova.", "Seu pedido mencionado foi o 78421."]
    )
    monkeypatch.setattr(
        chain_module, "ChatOllama", lambda model, temperature: fake_llm
    )

    conversa = chain_module.build_conversation_chain()

    resposta1 = conversa.predict(input="Oi, meu pedido e o 78421.")
    assert resposta1 == "Oi! Sou a Ana, da TechNova."

    resposta2 = conversa.predict(input="Qual pedido eu mencionei mesmo?")
    assert resposta2 == "Seu pedido mencionado foi o 78421."

    historico = conversa.memory.load_memory_variables({})["history"]
    # os 2 turnos (humano + IA) de cada troca devem estar na memoria
    assert len(historico) >= 4


def test_analise_chain_retorna_analise_solicitacao_valida(monkeypatch):
    monkeypatch.setenv("OLLAMA_API_KEY", "chave-de-teste")
    resposta_json = json.dumps(
        {
            "categoria": "status_pedido",
            "urgencia": "alta",
            "sentimento": "negativo",
            "produto_mencionado": "Fone XPTO",
            "resumo": "Cliente reclama que o pedido do fone XPTO nao chegou.",
            "acao_recomendada": "Verificar rastreio e responder o cliente com urgencia.",
        }
    )
    fake_llm = FakeChatModel(responses=[resposta_json])
    monkeypatch.setattr(
        chain_module, "ChatOllama", lambda model, temperature: fake_llm
    )

    analise_chain = chain_module.build_analise_chain()
    resultado = analise_chain.invoke({"input": "Meu fone XPTO nao chegou, ja faz 1 semana!"})

    assert isinstance(resultado, AnaliseSolicitacao)
    assert resultado.categoria == "status_pedido"
    assert resultado.urgencia == "alta"
    assert resultado.produto_mencionado == "Fone XPTO"
