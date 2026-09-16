"""Demonstração de "context rot": a mesma pergunta é feita ao modelo com
quantidades crescentes de contexto (turnos de conversa) na frente dela, para
mostrar como a qualidade da resposta se degrada conforme o contexto cresce.

Rodar diretamente: `python -m app.context_rot`
Gera uma tabela no console e, se `tiktoken` estiver disponível, também a
contagem de tokens de cada janela testada (diferencial de +0,5).
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.chain import build_llm
from app.prompts import SYSTEM_PROMPT

# Pergunta fixa, cuja resposta certa é conhecida, usada em todas as janelas.
PERGUNTA_TESTE = (
    "Qual era a minha meta de economia mensal mesmo, que eu falei no começo "
    "da nossa conversa?"
)
META_CORRETA = "500"

# "Ruído" de contexto: turnos de conversa irrelevantes inseridos entre o dado
# importante (meta de R$500/mês, mencionada no primeiro turno) e a pergunta final.
TURNO_COM_DADO = (
    HumanMessage(
        content=f"Oi, minha meta é economizar R${META_CORRETA} por mês para viajar."
    ),
    AIMessage(
        content="Que meta legal! Vamos ver juntos como organizar seu orçamento para isso."
    ),
)

# Pool de turnos de "ruído" variados — inclui distratores com OUTROS valores de
# meta/economia parecidos com o dado real (R$500), para testar se o modelo
# confunde o número certo com um dos números mencionados depois. Ruído
# idêntico e repetitivo é fácil demais de ignorar; distratores plausíveis são
# o que de fato estressa a memória em contextos longos.
TURNOS_RUIDO_POOL = (
    (
        HumanMessage(content="O que é melhor, Tesouro Direto ou poupança?"),
        AIMessage(
            content="De forma geral, o Tesouro Direto costuma render mais que a poupança, mas cada opção tem características diferentes de liquidez e risco."
        ),
    ),
    (
        HumanMessage(
            content="Minha prima falou que a meta de economia dela é R$300 por mês, isso é bastante?"
        ),
        AIMessage(
            content="Depende da renda dela — R$300 por mês pode ser um ótimo começo ou pouco, dependendo do orçamento total."
        ),
    ),
    (
        HumanMessage(content="Estou com uma dívida de R$2000 no cartão de crédito."),
        AIMessage(
            content="Entendo. Uma boa estratégia é priorizar essa dívida, já que o juro do cartão costuma ser um dos mais altos."
        ),
    ),
    (
        HumanMessage(
            content="Ano passado eu tinha uma meta de guardar R$800 por mês, mas não consegui."
        ),
        AIMessage(
            content="Sem problemas, metas podem ser ajustadas. O importante é revisar o orçamento e tentar de novo com um valor realista."
        ),
    ),
    (
        HumanMessage(content="O que é CDB e vale a pena?"),
        AIMessage(
            content="CDB é um título de renda fixa emitido por bancos. Pode valer a pena dependendo da taxa e do prazo, sempre comparando com o CDI."
        ),
    ),
    (
        HumanMessage(
            content="Um amigo meu economiza R$150 por mês desde janeiro para uma reserva de emergência."
        ),
        AIMessage(
            content="Que legal! Reserva de emergência costuma ser a primeira meta recomendada antes de outros objetivos."
        ),
    ),
    (
        HumanMessage(content="Vale a pena antecipar parcelas de financiamento?"),
        AIMessage(
            content="Geralmente sim, se o juro do financiamento for maior que o rendimento de uma aplicação, mas depende do seu fluxo de caixa."
        ),
    ),
    (
        HumanMessage(
            content="Também considerei economizar R$650 por mês em vez de outro valor, o que acha?"
        ),
        AIMessage(
            content="R$650 é um valor mais ambicioso — só recomendo se ele couber confortavelmente no seu orçamento mensal."
        ),
    ),
)


@dataclass
class ResultadoJanela:
    n_turnos_ruido: int
    n_tokens: int | None
    resposta: str
    acertou: bool
    tempo_resposta_s: float


def _montar_historico(n_turnos_ruido: int) -> list:
    historico = list(TURNO_COM_DADO)
    for i in range(n_turnos_ruido):
        par = TURNOS_RUIDO_POOL[i % len(TURNOS_RUIDO_POOL)]
        historico.extend(par)
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
    inicio = time.perf_counter()
    resposta = chain.invoke({"history": historico, "input": PERGUNTA_TESTE})
    tempo_resposta_s = time.perf_counter() - inicio
    texto_resposta = resposta.content

    return ResultadoJanela(
        n_turnos_ruido=n_turnos_ruido,
        n_tokens=_contar_tokens(historico, PERGUNTA_TESTE),
        resposta=texto_resposta,
        acertou=META_CORRETA in texto_resposta,
        tempo_resposta_s=tempo_resposta_s,
    )


def rodar_experimento(
    janelas: tuple[int, ...] = (0, 30, 100, 200, 300, 500)
) -> list[ResultadoJanela]:
    return [rodar_janela(n) for n in janelas]


def imprimir_tabela(resultados: list[ResultadoJanela]) -> None:
    print(f"{'Turnos ruído':>12} | {'Tokens':>8} | {'Acertou?':>9} | {'Tempo (s)':>9} | Resposta")
    print("-" * 100)
    for r in resultados:
        tokens = r.n_tokens if r.n_tokens is not None else "n/d"
        print(
            f"{r.n_turnos_ruido:>12} | {tokens!s:>8} | {'sim' if r.acertou else 'não':>9} "
            f"| {r.tempo_resposta_s:>9.2f} | {r.resposta[:50]}"
        )


def gerar_grafico(
    resultados: list[ResultadoJanela], caminho: str = "context_rot_grafico.png"
) -> str:
    """Plota tokens (eixo x) vs. taxa de acerto e tempo de resposta (eixo y duplo).

    Diferencial de +0,5 (context engineering com métricas). Requer `matplotlib`.
    """
    import matplotlib.pyplot as plt

    tokens = [r.n_tokens for r in resultados if r.n_tokens is not None]
    acertos = [100 if r.acertou else 0 for r in resultados if r.n_tokens is not None]
    tempos = [r.tempo_resposta_s for r in resultados if r.n_tokens is not None]

    fig, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(tokens, acertos, marker="o", color="#1f77b4", label="Acertou (%)")
    ax1.set_xlabel("Tokens de contexto")
    ax1.set_ylabel("Acertou a pergunta? (100 = sim, 0 = não)", color="#1f77b4")
    ax1.set_ylim(-10, 110)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(tokens, tempos, marker="s", color="#d62728", label="Tempo de resposta (s)")
    ax2.set_ylabel("Tempo de resposta (s)", color="#d62728")

    ax1.set_title("Context rot — qualidade e latência x tamanho do contexto")
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
    return caminho


if __name__ == "__main__":
    resultados = rodar_experimento()
    imprimir_tabela(resultados)
    caminho_grafico = gerar_grafico(resultados)
    print(f"\nGráfico salvo em: {caminho_grafico}")
