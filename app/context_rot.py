"""Demonstração de "context rot": a mesma pergunta é feita ao modelo com
quantidades crescentes de contexto (turnos de conversa) na frente dela, para
mostrar como a qualidade da resposta se degrada conforme o contexto cresce.

Rodar diretamente: `python -m app.context_rot`
Gera uma tabela no console e, se `tiktoken` estiver disponível, também a
contagem de tokens de cada janela testada (diferencial de +0,5).
"""

from __future__ import annotations

from dataclasses import dataclass

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.chain import build_llm
from app.prompts import SYSTEM_PROMPT

# Pergunta fixa, cuja resposta certa é conhecida, usada em todas as janelas.
PERGUNTA_TESTE = (
    "Qual foi o número do pedido que eu mencionei no começo da nossa conversa?"
)
PEDIDO_CORRETO = "78421"

# "Ruído" de contexto: turnos de conversa irrelevantes inseridos entre o dado
# importante (pedido 78421, mencionado no primeiro turno) e a pergunta final.
TURNO_COM_DADO = (
    HumanMessage(content=f"Oi, meu pedido é o {PEDIDO_CORRETO}, ele ainda não chegou."),
    AIMessage(content="Entendi, sinto muito pelo atraso. Vou verificar isso para você."),
)

TURNOS_RUIDO = (
    HumanMessage(content="Vocês têm fones de ouvido sem fio na loja?"),
    AIMessage(content="Sim! Temos alguns modelos com cancelamento de ruído."),
)


@dataclass
class ResultadoJanela:
    n_turnos_ruido: int
    n_tokens: int | None
    resposta: str
    acertou: bool


def _montar_historico(n_turnos_ruido: int) -> list:
    historico = list(TURNO_COM_DADO)
    for _ in range(n_turnos_ruido):
        historico.extend(TURNOS_RUIDO)
    return historico


def _contar_tokens(mensagens: list, pergunta: str) -> int | None:
    try:
        import tiktoken
    except ImportError:
        return None

    enc = tiktoken.get_encoding("cl100k_base")
    texto = SYSTEM_PROMPT + pergunta + "".join(m.content for m in mensagens)
    return len(enc.encode(texto))


def rodar_janela(n_turnos_ruido: int) -> ResultadoJanela:
    llm = build_llm(temperature=0.0)
    historico = _montar_historico(n_turnos_ruido)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm
    resposta = chain.invoke({"history": historico, "input": PERGUNTA_TESTE})
    texto_resposta = resposta.content

    return ResultadoJanela(
        n_turnos_ruido=n_turnos_ruido,
        n_tokens=_contar_tokens(historico, PERGUNTA_TESTE),
        resposta=texto_resposta,
        acertou=PEDIDO_CORRETO in texto_resposta,
    )


def rodar_experimento(janelas: tuple[int, ...] = (0, 5, 10, 15, 20)) -> list[ResultadoJanela]:
    return [rodar_janela(n) for n in janelas]


def imprimir_tabela(resultados: list[ResultadoJanela]) -> None:
    print(f"{'Turnos ruído':>12} | {'Tokens':>8} | {'Acertou?':>9} | Resposta")
    print("-" * 80)
    for r in resultados:
        tokens = r.n_tokens if r.n_tokens is not None else "n/d"
        print(f"{r.n_turnos_ruido:>12} | {tokens!s:>8} | {'sim' if r.acertou else 'não':>9} | {r.resposta[:60]}")


if __name__ == "__main__":
    resultados = rodar_experimento()
    imprimir_tabela(resultados)
