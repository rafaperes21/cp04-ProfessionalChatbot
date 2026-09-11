"""Schemas Pydantic v2 usados para validar saídas estruturadas do chatbot."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AnaliseConsulta(BaseModel):
    """Análise estruturada de uma mensagem do usuário, gerada pela Chain 2 (LCEL)."""

    categoria: Literal[
        "orcamento",
        "divida",
        "investimento_educacional",
        "planejamento_meta",
        "duvida_conceito",
        "outro",
    ] = Field(..., description="Categoria principal da consulta financeira.")

    urgencia: Literal["baixa", "media", "alta"] = Field(
        ..., description="Urgência percebida da consulta."
    )

    sentimento: Literal["positivo", "neutro", "negativo"] = Field(
        ..., description="Sentimento predominante na mensagem do usuário."
    )

    topico_mencionado: Optional[str] = Field(
        default=None,
        description="Tópico financeiro específico mencionado (ex: cartão de crédito, reserva de emergência).",
    )

    resumo: str = Field(..., description="Resumo da consulta em uma frase.")

    acao_recomendada: str = Field(
        ..., description="Próxima ação recomendada para o time de suporte."
    )
