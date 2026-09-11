"""As duas chains da Aula 03:

1. `build_conversation_chain` — ConversationChain com memória, usada para o
   chat com o cliente.
2. `build_analise_chain` — pipeline LCEL (prompt | llm | parser) que produz
   uma saída estruturada e validada (AnaliseSolicitacao) a partir da mesma
   mensagem do usuário.
"""

import os

from dotenv import load_dotenv
from langchain.chains import ConversationChain
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

from app.memory_manager import build_memory
from app.prompts import ANALISE_SYSTEM_PROMPT, SYSTEM_PROMPT
from app.schemas import AnaliseSolicitacao

load_dotenv()

MODEL_NAME = "gemma4:cloud"


def build_llm(temperature: float = 0.4) -> ChatOllama:
    """Instancia o ChatOllama apontando exclusivamente para gemma4:cloud.

    A chave `OLLAMA_API_KEY` é lida do ambiente (via .env + python-dotenv) e
    deve estar configurada no processo/host que atende a Ollama Cloud —
    confirme com o material da disciplina o passo exato de autenticação da
    conta Ollama Cloud usada pelo grupo.
    """
    if not os.getenv("OLLAMA_API_KEY"):
        raise RuntimeError(
            "OLLAMA_API_KEY não encontrada. Copie .env.example para .env e "
            "preencha com sua chave da Ollama Cloud."
        )
    return ChatOllama(model=MODEL_NAME, temperature=temperature)


def build_conversation_chain() -> ConversationChain:
    """Chain 1 — conversa com o cliente, com memória gerenciada."""
    llm = build_llm(temperature=0.4)
    memory = build_memory(llm)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    return ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        input_key="input",
        verbose=False,
    )


def build_analise_chain():
    """Chain 2 — pipeline LCEL que retorna um AnaliseSolicitacao validado."""
    llm = build_llm(temperature=0.0)
    parser = PydanticOutputParser(pydantic_object=AnaliseSolicitacao)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ANALISE_SYSTEM_PROMPT + "\n{format_instructions}"),
            ("human", "{input}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    return prompt | llm | parser
