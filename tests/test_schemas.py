"""Testes do schema Pydantic v2 AnaliseConsulta."""

import pytest
from pydantic import ValidationError

from app.schemas import AnaliseConsulta


def test_analise_consulta_valida():
    obj = AnaliseConsulta(
        categoria="orcamento",
        urgencia="baixa",
        sentimento="neutro",
        topico_mencionado="cartao de credito",
        resumo="Usuario quer ajuda para organizar o orcamento mensal.",
        acao_recomendada="Sugerir listar gastos fixos e variaveis.",
    )
    assert obj.categoria == "orcamento"
    assert obj.topico_mencionado == "cartao de credito"


def test_topico_mencionado_e_opcional():
    obj = AnaliseConsulta(
        categoria="duvida_conceito",
        urgencia="baixa",
        sentimento="positivo",
        resumo="Usuario perguntou o que e Tesouro Direto.",
        acao_recomendada="Explicar o conceito de forma educativa.",
    )
    assert obj.topico_mencionado is None


def test_categoria_invalida_gera_erro():
    with pytest.raises(ValidationError):
        AnaliseConsulta(
            categoria="categoria_que_nao_existe",
            urgencia="baixa",
            sentimento="neutro",
            resumo="x",
            acao_recomendada="y",
        )


def test_campo_obrigatorio_faltando_gera_erro():
    with pytest.raises(ValidationError):
        AnaliseConsulta(categoria="outro", urgencia="baixa", sentimento="neutro")
