from llama_cpp import Llama

# путь к модели .gguf
model_path = "Phi-3-mini-4k-instruct-q4.gguf"

# загружаем модель
llm = Llama(
    model_path=model_path,
    n_ctx=4096,
    n_threads=8,
    verbose=False
)

print("🤖 Phi-3 Mini Chat (введи 'exit' чтобы выйти)\n")

messages = [{"role": "system", "content": "You are a helpful assistant."}]

while True:
    user_input = input("👤 You: ")
    if user_input.lower() in {"exit", "quit"}:
        break

    messages.append({"role": "user", "content": user_input})
    print("🤖 Bot: ", end="", flush=True)

    # стримим ответ по частям
    stream = llm.create_chat_completion(
        messages=messages,
        max_tokens=200,
        temperature=0.7,
        stream=True
    )

    reply = ""
    for chunk in stream:
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            text = delta["content"]
            reply += text
            print(text, end="", flush=True)

    print("\n")
    messages.append({"role": "assistant", "content": reply})

