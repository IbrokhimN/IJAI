from llama_cpp import Llama

# Настройка модели 
MODEL_PATH = "Yi-1.5-6B-Chat-Q4_K_M.gguf"

# Загружаем Yi один раз при импорте
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_threads=8,
    verbose=False
)

# Контекст чата (можно сохранять, если хочешь диалог)
messages = [{"role": "system", "content": "You are a helpful assistant."}]

def ask_yi(prompt: str, max_tokens: int = 200, temperature: float = 0.7):
    """
    Стриминговый вызов Yi.
    Возвращает полный ответ, а также печатает куски в реальном времени.

    Пример:
        from yi_stream import ask_yi
        text = ask_yi("Привет, расскажи что-нибудь интересное!")
        print("Полный ответ:", text)
    """
    messages.append({"role": "user", "content": prompt})
    print("", end="", flush=True)

    reply = ""
    stream = llm.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True
    )

    for chunk in stream:
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            text = delta["content"]
            reply += text
            # выводим кусочек без переноса строки
            print(text, end="", flush=True)

    print()  # финальный перенос строки
    messages.append({"role": "assistant", "content": reply})
    return reply

