"""Geração da resposta final com gemma4:cloud, fundamentada no contexto recuperado."""

import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

load_dotenv()

SYSTEM_PROMPT = """\
<papel>
Você é o DocMind, um assistente que responde perguntas sobre educação
financeira pessoal usando EXCLUSIVAMENTE os trechos de documentos oficiais
fornecidos abaixo como contexto.
</papel>

<regras>
1. Responda apenas com base no contexto fornecido — nunca use conhecimento
   próprio para completar lacunas.
2. Se o contexto tiver informação relevante para a pergunta, responda
   diretamente com ela, sem ressalvas sobre o que o contexto "não detalha"
   — vá direto ao que ele realmente diz.
3. Só diga que não encontrou a informação se o contexto não tiver
   NADA relevante para a pergunta — não invente, mas também não hedge
   quando já existe conteúdo relevante para usar.
4. Ao final da resposta, cite a fonte entre colchetes, no formato
   [Fonte: nome_do_documento].
5. Responda em português do Brasil, de forma objetiva.
</regras>

<contexto>
{contexto}
</contexto>
"""


def build_llm(temperature: float = 0.0) -> ChatOllama:
    if not os.getenv("OLLAMA_API_KEY"):
        raise RuntimeError(
            "OLLAMA_API_KEY não encontrada. Copie .env.example para .env e "
            "preencha com sua chave da Ollama Cloud."
        )
    return ChatOllama(model="gemma4:cloud", temperature=temperature)


def gerar_resposta(pergunta: str, chunks_relevantes: list[dict]) -> str:
    contexto = "\n\n".join(
        f"[{c['metadata']['fonte']}] {c['texto']}" for c in chunks_relevantes
    )
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "{pergunta}")]
    )
    chain = prompt | build_llm()
    resposta = chain.invoke({"contexto": contexto, "pergunta": pergunta})
    return resposta.content
