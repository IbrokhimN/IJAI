from pathlib import Path
from llama_cpp import Llama
import re, time

# base paths and model file
BASE = Path(__file__).resolve().parent
MODEL_PATH = BASE / "gemma-7b.Q4_K_M.gguf"

llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=8192,
    n_threads=8,
    verbose=False
)

messages = [{"role": "system", "content": "You are a helpful assistant."}]
def format_chat(messages):
    formatted = ""
    for msg in messages:
        if msg["role"] == "system":
            formatted += f"<start_of_turn>system\n{msg['content']}<end_of_turn>\n"
        elif msg["role"] == "user":
            formatted += f"<start_of_turn>user\n{msg['content']}<end_of_turn>\n"
        elif msg["role"] == "assistant":
            formatted += f"<start_of_turn>model\n{msg['content']}<end_of_turn>\n"
    formatted += "<start_of_turn>model\n"
    return formatted

# remove boring repeated words like a human's attention span
def clean_repetitions(text: str) -> str:
    text = re.sub(r"\b(\w+)(?: \1){3,}\b", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"(?:\b\w+\b\s*){15,}", lambda m: " ".join(m.group(0).split()[:10]), text)
    return text.strip()

# generate a full reply, attempt to auto-continue if model bails
def ask(prompt: str, max_tokens: int = 2048, temperature: float = 0.7, auto_continue: bool = True) -> str:
    reply = ""
    for token in ask_stream(prompt, max_tokens=max_tokens, temperature=temperature):
        reply += token

    reply = clean_repetitions(reply)

    # if it cut off mid-sentence, ask it to continue
    if auto_continue and not reply.endswith(('.', '!', '?')) and len(reply.strip()) > 100:
        continuation = ""
        for token in ask_stream("continue", max_tokens=max_tokens//2, temperature=temperature):
            continuation += token
        reply += clean_repetitions(continuation)

    return reply

# stream tokens from the model with simple loop protection
def ask_stream(prompt: str, max_tokens: int = 2048, temperature: float = 0.7):
    global messages
    messages.append({"role": "user", "content": prompt})
    prompt_text = format_chat(messages)

    def generate():
        return llm.create_completion(
            prompt=prompt_text,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.95,
            stream=True,
            stop=["<end_of_turn>", "\n<start_of_turn>"]
        )

    stream = generate()
    reply, last_chunk, repeat_counter = "", "", 0
    last_token_time = time.time()

    for chunk in stream:
        text = chunk["choices"][0]["text"]
        reply += text
        now = time.time()

        if now - last_token_time > 15:
            print("\nМодель зависла — пробуем продолжить…")
            for t in ask_stream("continue", max_tokens=max_tokens//2, temperature=temperature):
                yield t
            return
        last_token_time = now
        if text.strip() == last_chunk.strip() and text.strip() != "":
            repeat_counter += 1
        else:
            repeat_counter = 0
        last_chunk = text

        if repeat_counter >= 10:
            print("\nОбнаружен зацикленный вывод. Продолжаем с новой подсказкой.")
            for t in ask_stream("continue", max_tokens=max_tokens//2, temperature=temperature):
                yield t
            return

        cleaned = clean_repetitions(reply)
        if cleaned != reply:
            reply = cleaned
            print("\rПовторы вычищены...", end="", flush=True)

        yield text

    reply = clean_repetitions(reply)
    messages.append({"role": "assistant", "content": reply})

    if len(messages) > 12:
        messages = [messages[0]] + messages[-10:]

# full history wipe, like a fresh nap
def reset_history():
    global messages
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
