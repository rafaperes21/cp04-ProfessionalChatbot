"""Testes das 2 chains (app/chain.py) usando um ChatOllama falso.

Nao fazem nenhuma chamada de rede: substituem `app.chain.ChatOllamaComContagemDeTokens`
por um FakeChatModel para validar a fiacao (wiring) do pipeline LCEL, da
ConversationChain com memoria, e do PydanticOutputParser.
"""

import json

import pytest

import app.chain as chain_module
from app.schemas import AnaliseConsulta
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

    monkeypatch.setattr(chain_module, "ChatOllamaComContagemDeTokens", ChatOllamaFalso)

    chain_module.build_llm(temperature=0.7)

    assert capturado["model"] == "gemma4:cloud"
    assert capturado["temperature"] == 0.7


def test_conversation_chain_responde_e_lembra_turnos(monkeypatch):
    monkeypatch.setenv("OLLAMA_API_KEY", "chave-de-teste")
    fake_llm = FakeChatModel(
        responses=["Oi! Sou a Fê, da FinComigo.", "Sua meta mencionada foi economizar R$500 por mês."]
    )
    monkeypatch.setattr(
        chain_module, "ChatOllamaComContagemDeTokens", lambda model, temperature: fake_llm
    )

    conversa = chain_module.build_conversation_chain()

    resposta1 = conversa.predict(input="Oi, minha meta é economizar R$500 por mês.")
    assert resposta1 == "Oi! Sou a Fê, da FinComigo."

    resposta2 = conversa.predict(input="Qual era minha meta mesmo?")
    assert resposta2 == "Sua meta mencionada foi economizar R$500 por mês."

    historico = conversa.memory.load_memory_variables({})["history"]
    # os 2 turnos (humano + IA) de cada troca devem estar na memoria
    assert len(historico) >= 4


def test_analise_chain_retorna_analise_consulta_valida(monkeypatch):
    monkeypatch.setenv("OLLAMA_API_KEY", "chave-de-teste")
    resposta_json = json.dumps(
        {
            "categoria": "divida",
            "urgencia": "alta",
            "sentimento": "negativo",
            "topico_mencionado": "cartão de crédito",
            "resumo": "Usuário está com dívida no cartão de crédito e não sabe como sair.",
            "acao_recomendada": "Explicar estratégia de priorização de dívidas por juros.",
        }
    )
    fake_llm = FakeChatModel(responses=[resposta_json])
    monkeypatch.setattr(
        chain_module, "ChatOllamaComContagemDeTokens", lambda model, temperature: fake_llm
    )

    analise_chain = chain_module.build_analise_chain()
    resultado = analise_chain.invoke(
        {"input": "Estou muito endividado no cartão de crédito, não sei o que fazer."}
    )

    assert isinstance(resultado, AnaliseConsulta)
    assert resultado.categoria == "divida"
    assert resultado.urgencia == "alta"
    assert resultado.topico_mencionado == "cartão de crédito"
