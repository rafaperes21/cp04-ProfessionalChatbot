# Próximos Passos — CKP01 Chatbot Profissional

Documento vivo com o que falta fazer para fechar a entrega. Complementa o
[PLANO_ACAO.md](PLANO_ACAO.md) (visão geral) e as
[milestones do GitHub](https://github.com/rafaperes21/cp04-ProfessionalChatbot/milestones)
(rastreamento).

## Status: trabalho técnico concluído ✅

Todos os requisitos obrigatórios e os dois diferenciais (+1,0) estão
implementados, testados com o modelo real (`gemma4:cloud`) e documentados no
`README.md` com evidência (tabelas, transcrições, gráfico):

- [x] Pipeline LCEL (chain.py) — validado com 5 categorias de mensagem reais
- [x] Memória gerenciada (`ConversationTokenBufferMemory`) — 6 turnos reais, reteve 2 dados distintos
- [x] Pydantic v2 (`AnaliseConsulta`) — validado sem erro de parsing em produção
- [x] Context rot — 6 janelas reais (0 a 500 turnos, até 25,6 mil tokens), tabela + gráfico + conclusão honesta
- [x] System prompt / persona — 5 tentativas de jailbreak reais, todas recusadas
- [x] Diferencial: gráfico tokens × qualidade × latência (`context_rot_grafico.png`)
- [x] Diferencial: meta prompting real, antes/depois documentado
- [x] Ambiente limpo testado agora mesmo: clone novo + venv novo + `pip install` do zero → 14/14 testes passando, `python -m app.main` sobe sem erro
- [x] README completo, sem placeholders, com os 6 integrantes/RMs e divisão de responsabilidades
- [x] Todas as issues técnicas fechadas no GitHub ([#2](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/2), [#3](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/3), [#4](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/4), [#5](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/5), [#6](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/6), [#7](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/7), [#8](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/8), [#9](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/9), [#10](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/10), [#11](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/11), [#12](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/12), [#13](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/13))

## O que falta — só 3 itens, todos administrativos/manuais

### 1. Registrar o domínio no Portal — [#1](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/1)

Domínio já confirmado e implementado: **educação financeira pessoal
("FinComigo")**. Falta só o registro oficial no Portal da FIAP (ação da Aula
01) — quem registrar primeiro garante o domínio; grupos duplicados só têm o
primeiro aceito. O local exato de registro não está detalhado no enunciado —
procurem o formulário/campo da tarefa do CKP01 no ambiente da disciplina ou
perguntem ao Prof. Jorge Luiz Gomes. **Isso é uma ação manual do grupo, não
dá pra automatizar.**

### 2. Montar e revisar o zip de entrega — [#14](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/14)

```bash
cd E:\FIAP\cp04-
```

Gerar `CKP01_educacao-financeira_grupo.zip` (ou nome similar) contendo:
- `app/` (com `assets/icon.png` incluso)
- `.env.example`
- `requirements.txt`
- `README.md`

Checklist antes de fechar o zip:
- [ ] **`.env` NÃO está incluído** (contém a chave — confirmar antes de zipar)
- [ ] `.venv/`, `__pycache__/`, `.pytest_cache/` não estão incluídos
- [ ] Testar que o zip abre e os arquivos batem com o repositório

### 3. Entrega via Teams — [#15](https://github.com/rafaperes21/cp04-ProfessionalChatbot/issues/15)

Somente o líder do grupo envia o `.zip`, na tarefa aberta pelo professor no
Teams, até 23:55 do dia da Aula 05. Se houver atraso, falar com o professor
**antes** do prazo.
