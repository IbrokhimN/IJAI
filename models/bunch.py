import os
import sys
import functools
from pathlib import Path
from llama_cpp import Llama
from tts.edgetts.edgetts import speech_queue, start_tts

# Always flush stdout to avoid buffering issues in interactive mode.
print = functools.partial(print, flush=True)

# Path to the quantized LLaMA model. Adjust if you move the model.
MODEL_PATH = str(Path("~/IJAI/models/llm/yi-1.5-6b-chat-q4/Yi-1.5-6B-Chat-Q4_K_M.gguf").expanduser())

class SilentStdErr:
    """
    Context manager to temporarily silence stderr.
    Useful for noisy libraries (looking at you, llama_cpp).
    """
    def __enter__(self):
        self.stderr_fd = os.dup(2)              # Save current stderr
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.devnull, 2)                # Redirect stderr to /dev/null
        return self
    def __exit__(self, *a):
        os.dup2(self.stderr_fd, 2)              # Restore stderr
        os.close(self.devnull)
        os.close(self.stderr_fd)

# Make sure the model is actually there. Don't waste CPU cycles otherwise.
if not Path(MODEL_PATH).exists():
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

# Kick off TTS in a separate thread. Let it run; we don't care how.
start_tts()

# Load the LLaMA model with stderr muted to avoid spam from ggml internals.
with SilentStdErr():
    llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4)

print("💬 Enter a prompt. Type 'exit' or Ctrl+C to quit.")

# Main REPL loop: ask, generate, speak, repeat.
while True:
    try:
        prompt = input("\n👉 Your input: ")
        if prompt.strip().lower() in ["exit", "quit"]:
            break

        buffer = ""  # Holds generated text until a full sentence is ready for TTS.

        # Stream tokens as they come in; silence any llama_cpp whining.
        with SilentStdErr():
            for chunk in llm.create_chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    stream=True):
                delta = chunk["choices"][0]["delta"].get("content", "")
                if delta:
                    print(delta, end="", flush=True)
                    buffer += delta
                    # Send sentence to TTS as soon as it looks complete.
                    if any(buffer.endswith(end) for end in [".", "!", "?"]):
                        speech_queue.put(buffer.strip())
                        buffer = ""

        # Send whatever's left if it doesn't end in punctuation.
        if buffer.strip():
            speech_queue.put(buffer.strip())

        print()
    except KeyboardInterrupt:
        print("\nExiting chat...")
        break

# Tell the TTS thread to shut down gracefully.
speech_queue.put(None)
