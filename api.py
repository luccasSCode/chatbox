import streamlit as st

from config import (
    APP_TITLE,
    APP_ICON,
    APP_DESCRIPTION,
    SYSTEM_PROMPT_PADRAO
)

from ollama_service import (
    listar_modelos,
    preparar_mensagens,
    gerar_resposta
)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="centered"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = SYSTEM_PROMPT_PADRAO


def nova_conversa():
    st.session_state.messages = []


def contar_mensagens_usuario():
    total = 0
    for mensagem in st.session_state.messages:
        if mensagem["role"] == "user":
            total += 1
    return total


st.title(f"{APP_ICON} {APP_TITLE}")
st.caption("ChatBot com Ollama")
st.write(APP_DESCRIPTION)

modelos = listar_modelos()

with st.sidebar:
    st.header("Configurações")
    st.divider()
    st.subheader("Inteligência Artificial")

    if modelos:
        modelo_selecionado = st.selectbox(
            "Escolha o Modelo",
            modelos
        )
        st.success(f"Modelo selecionado: \n\n{modelo_selecionado}")
    else:
        modelo_selecionado = None
        st.error("Nenhum modelo foi encontrado no Ollama")
        st.error("Instale um modelo usando:")
        st.code("ollama pull qwen3:4b", language="bash")

    st.divider()
    st.subheader("System Prompt")
    system_prompt = st.text_area(
        "Comportamento da IA",
        value=st.session_state.system_prompt,
        height=250
    )
    st.session_state.system_prompt = system_prompt

    st.divider()
    st.subheader("Conversa")
    total_mensagens_usuario = contar_mensagens_usuario()

    st.metric(
        "Mensagens Enviadas",
        total_mensagens_usuario
    )
    if st.button(
        "Nova Conversa",
        use_container_width=True
    ):
        nova_conversa()
        st.rerun()

if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown(
            """
            Olá,
            Sou o assistente de IA, chamado Oona.
            Escolha o modelo na barra lateral e me faça uma pergunta.
            O que iremos desvendar hoje?
            """
        )

for mensagem in st.session_state.messages:
    role = mensagem["role"]
    content = mensagem["content"]

    with st.chat_message(role):
        st.markdown(content)

        if role == "assistant" and "model" in mensagem:
            st.caption(f"Modelo: {mensagem['model']}")

prompt = st.chat_input("Digite sua mensagem ...")

if prompt:
    if modelo_selecionado is None:
        st.error("Nenhum modelo disponível.")
        st.info("Instale um modelo Ollama antes de continuar.")
        st.stop()

    mensagem_usuario = {
        "role": "user",
        "content": prompt
    }
    st.session_state.messages.append(mensagem_usuario)

    with st.chat_message("user"):
        st.markdown(prompt)

    mensagens_ollama = preparar_mensagens(
        st.session_state.system_prompt,
        st.session_state.messages
    )

    with st.chat_message("assistant"):
        try:
            resposta_completa = st.write_stream(
                gerar_resposta(
                    modelo_selecionado,
                    mensagens_ollama
                )
            )
            st.caption(f"Modelo: {modelo_selecionado}")
        except Exception as erro:
            st.error("Erro ao comunicar com o Ollama")
            st.exception(erro)
            resposta_completa = None

    if resposta_completa:
        mensagem_assistente = {
            "role": "assistant",
            "content": resposta_completa,
            "model": modelo_selecionado
        }
        st.session_state.messages.append(mensagem_assistente)
