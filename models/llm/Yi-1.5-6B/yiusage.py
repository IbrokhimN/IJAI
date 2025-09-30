from llama_cpp import Llama

# === Model setup ===
# Path to the quantized Yi model. If it's wrong, nothing will work. Fix it.
MODEL_PATH = "Yi-1.5-6B-Chat-Q4_K_M.gguf"

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,     # Context size. Bigger = more memory, more history.
    n_threads=8,    # Use your CPU. Otherwise, why did you buy it?
    verbose=False   # Silence useless ggml logs.
)

# Keep history if you want multi-turn conversations.
messages = [{"role": "system", "content": "You are a helpful assistant."}]

def ask_yi(prompt: str, max_tokens: int = 200, temperature: float = 0.7):
    """
    Stream a response from Yi while printing chunks in real-time.

    Args:
        prompt (str): User input.
        max_tokens (int): Token budget for this response.
        temperature (float): Higher = more random output.

    Returns:
        str: Full concatenated reply.

    Example:
        from yi_stream import ask_yi
        text = ask_yi("Hello, tell me something fun!")
        print("Full answer:", text)
    """
    # Add user message to the running history.
    messages.append({"role": "user", "content": prompt})
    print("", end="", flush=True)  # Make sure we start clean.

    reply = ""
    # Stream mode: Yi sends pieces as they are generated.
    stream = llm.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True
    )

    # Read chunks as they come in and print immediately.
    for chunk in stream:
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            text = delta["content"]
            reply += text
            print(text, end="", flush=True)  # No newline, we’re streaming.

    print()  

    # Save assistant reply so the next call keeps the context.
    messages.append({"role": "assistant", "content": reply})
    return reply
