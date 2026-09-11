"""Testes do schema Pydantic v2 AnaliseSolicitacao."""

import pytest
from pydantic import ValidationError

from app.schemas import AnaliseSolicitacao


def test_analise_solicitacao_valida():
    obj = AnaliseSolicitacao(
        categoria="duvida_produto",
        urgencia="baixa",
        sentimento="neutro",
        produto_mencionado="Fone XPTO",
        resumo="Cliente quer saber se o fone tem cancelamento de ruido.",
        acao_recomendada="Responder com as especificacoes do produto.",
    )
    assert obj.categoria == "duvida_produto"
    assert obj.produto_mencionado == "Fone XPTO"


def test_produto_mencionado_e_opcional():
    obj = AnaliseSolicitacao(
        categoria="elogio",
        urgencia="baixa",
        sentimento="positivo",
        resumo="Cliente elogiou o atendimento.",
        acao_recomendada="Agradecer o feedback.",
    )
    assert obj.produto_mencionado is None


def test_categoria_invalida_gera_erro():
    with pytest.raises(ValidationError):
        AnaliseSolicitacao(
            categoria="categoria_que_nao_existe",
            urgencia="baixa",
            sentimento="neutro",
            resumo="x",
            acao_recomendada="y",
        )


def test_campo_obrigatorio_faltando_gera_erro():
    with pytest.raises(ValidationError):
        AnaliseSolicitacao(categoria="outro", urgencia="baixa", sentimento="neutro")
