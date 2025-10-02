from pathlib import Path
from llama_cpp import Llama

# === Model setup ===
# Resolve path relative to this file. Stop relying on CWD.
BASE = Path(__file__).resolve().parent
MODEL_PATH = BASE / "Phi-3-mini-4k-instruct-q4.gguf"

llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=4096,     # Context size. Don’t crank it up unless you enjoy OOM errors.
    n_threads=8,    # Use your damn CPU. It’s not decoration.
    verbose=False   # Silence the useless spam from ggml.
)

# History — otherwise the model will act like it has dementia.
messages = [{"role": "system", "content": "You are a helpful assistant."}]

def ask(prompt: str, max_tokens: int = 200, temperature: float = 0.7):
    """
    Streams a response from Phi-3-mini in real time.

    Args:
        prompt (str): User input.
        max_tokens (int): Token budget.
        temperature (float): Creativity control.

    Returns:
        str: Full concatenated reply.
    """
    messages.append({"role": "user", "content": prompt})
    print("🤖 Bot: ", end="", flush=True)

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

