import ollama


def listar_modelos():
    try:
        resposta = ollama.list()
        modelos = []

        for modelo in resposta.models:
            modelos.append(modelo.model)

        return modelos

    except Exception as erro:
        print(f"Erro ao listar modelos: {erro}")
        return []


def preparar_mensagens(system_prompt, historico):
    mensagens = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    for mensagem in historico:
        mensagens.append(
            {
                "role": mensagem["role"],
                "content": mensagem["content"]
            }
        )
    return mensagens


def gerar_resposta(modelo, mensagens):
    stream = ollama.chat(
        model=modelo,
        messages=mensagens,
        stream=True
    )

    for parte in stream:
        texto = parte["message"]["content"]

        if texto:
            yield texto
