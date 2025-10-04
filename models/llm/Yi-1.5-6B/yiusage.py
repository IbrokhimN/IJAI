from pathlib import Path
from llama_cpp import Llama

BASE = Path(__file__).resolve().parent
MODEL_PATH = BASE / "Yi-1.5-6B-Chat-Q4_K_M.gguf"

llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=4096,
    n_threads=8,
    verbose=False
)

messages = [{"role": "system", "content": "You are a helpful assistant."}]

def ask(prompt: str, max_tokens: int = 200, temperature: float = 0.7):
    """
    Full (non-streaming) call for backward compatibility.
    """
    reply = ""
    for token in ask_stream(prompt, max_tokens=max_tokens, temperature=temperature):
        reply += token
    return reply


def ask_stream(prompt: str, max_tokens: int = 200, temperature: float = 0.7):
    messages.append({"role": "user", "content": prompt})
    stream = llm.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True
    )

    reply = ""
    for chunk in stream:
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            text = delta["content"]
            reply += text
            yield text  # возвращаем по кусочку
    messages.append({"role": "assistant", "content": reply})

