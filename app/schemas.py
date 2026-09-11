"""Schemas Pydantic v2 usados para validar saídas estruturadas do chatbot."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AnaliseSolicitacao(BaseModel):
    """Análise estruturada de uma mensagem de cliente, gerada pela Chain 2 (LCEL)."""

    categoria: Literal[
        "duvida_produto",
        "status_pedido",
        "troca_devolucao",
        "reclamacao",
        "elogio",
        "outro",
    ] = Field(..., description="Categoria principal da solicitação do cliente.")

    urgencia: Literal["baixa", "media", "alta"] = Field(
        ..., description="Urgência percebida da solicitação."
    )

    sentimento: Literal["positivo", "neutro", "negativo"] = Field(
        ..., description="Sentimento predominante na mensagem do cliente."
    )

    produto_mencionado: Optional[str] = Field(
        default=None, description="Nome do produto mencionado, se houver."
    )

    resumo: str = Field(..., description="Resumo da solicitação em uma frase.")

    acao_recomendada: str = Field(
        ..., description="Próxima ação recomendada para o time de suporte."
    )
