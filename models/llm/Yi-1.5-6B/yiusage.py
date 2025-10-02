from pathlib import Path
from llama_cpp import Llama

# === Model setup ===
# Always resolve path relative to this file, not current working dir.
BASE = Path(__file__).resolve().parent
MODEL_PATH = BASE / "Yi-1.5-6B-Chat-Q4_K_M.gguf"

# Load model once on import. If this fails, you screwed up your files.
llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=4096,
    n_threads=8,
    verbose=False
)

# Persistent chat history. Yes, it matters.
messages = [{"role": "system", "content": "You are a helpful assistant."}]

def ask(prompt: str, max_tokens: int = 200, temperature: float = 0.7):
    """
    Stream a response from Yi in real time.

    Args:
        prompt (str): User input.
        max_tokens (int): Maximum tokens to generate.
        temperature (float): Higher = more random output.

    Returns:
        str: The full reply.
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
            print(text, end="", flush=True)

    print()
    messages.append({"role": "assistant", "content": reply})
    return reply

