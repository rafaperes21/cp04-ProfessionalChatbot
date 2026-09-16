"""Meta prompting (técnica da Aula 04, diferencial de +0,5): usa o próprio
`gemma4:cloud` para criticar e sugerir melhorias no SYSTEM_PROMPT do chatbot.

Rodar diretamente: `python -m app.meta_prompting`
Imprime a crítica gerada pelo modelo. O antes/depois deve ser documentado
manualmente no README (seção "Meta prompting") após revisar as sugestões.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from app.chain import build_llm
from app.prompts import SYSTEM_PROMPT

CRITICA_SYSTEM_PROMPT = """\
Você é um revisor especialista em prompt engineering. Vai receber o system
prompt de um chatbot de educação financeira e deve:

1. Apontar até 3 pontos fracos concretos (ambiguidade, regra faltando,
   brecha que permitiria o chatbot sair do personagem ou dar conselho
   financeiro regulado).
2. Propor uma versão revisada das seções problemáticas, mantendo a
   formatação com tags XML (<persona>, <regras>, <restricoes>, <exemplos>).

Seja objetivo e específico — não repita o prompt inteiro, foque nas mudanças.
"""


def criticar_prompt(system_prompt: str = SYSTEM_PROMPT) -> str:
    llm = build_llm(temperature=0.2)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CRITICA_SYSTEM_PROMPT),
            ("human", "System prompt atual:\n\n{prompt}"),
        ]
    )
    chain = prompt | llm
    resposta = chain.invoke({"prompt": system_prompt})
    return resposta.content


if __name__ == "__main__":
    print(criticar_prompt())
