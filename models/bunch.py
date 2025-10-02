import os
import sys
import functools
import importlib.util
from pathlib import Path
from tts.edgetts.edgetts import speech_queue, start_tts

# Always flush stdout. Otherwise, enjoy invisible logs.
print = functools.partial(print, flush=True)

def load_module(module_name: str, file_path: str):
    """Load a Python module from an arbitrary file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Cannot find spec for {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

class SilentStdErr:
    """Context manager to silence stderr temporarily."""
    def __enter__(self):
        self.stderr_fd = os.dup(2)
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.devnull, 2)
        return self
    def __exit__(self, *a):
        os.dup2(self.stderr_fd, 2)
        os.close(self.devnull)
        os.close(self.stderr_fd)

# Base path
BASE = Path(__file__).resolve().parent
CHOICE_FILE = BASE / "model_choice.txt"

# Figure out which model to load
if CHOICE_FILE.exists():
    model_choice = CHOICE_FILE.read_text().strip()
    print(f"✅ Loaded previous choice: {model_choice}")
else:
    while True:
        choice = input("👉 Pick a model ('yi' or 'phi'): ").strip().lower()
        if choice in ["yi", "phi"]:
            model_choice = choice
            CHOICE_FILE.write_text(model_choice)
            break
        print("⚠️ Invalid choice. Type 'yi' or 'phi'.")

# Load only the chosen model
if model_choice == "yi":
    module_path = BASE / "llm/yi-1.5-6b-chat-q4/yiusage.py"
    engine = load_module("yiusage", str(module_path))
    print("🚀 Yi model loaded. Start chatting!")

elif model_choice == "phi":
    module_path = BASE / "llm/phi-3-mini/phiusage.py"
    engine = load_module("phiusage", str(module_path))
    print("🚀 Phi-3-mini model loaded. Start chatting!")

# Start TTS
start_tts()

print("💬 Type 'exit' or Ctrl+C to quit.")

while True:
    try:
        prompt = input("\n👤 You: ")
        if prompt.strip().lower() in ["exit", "quit"]:
            break

        # Use engine.ask(), it streams text itself
        with SilentStdErr():
            reply = engine.ask(prompt, max_tokens=200, temperature=0.7)

        # Send the final reply to TTS
        if reply.strip():
            speech_queue.put(reply.strip())

        print()
    except KeyboardInterrupt:
        print("\nExiting chat...")
        break

# Shut down TTS thread
speech_queue.put(None)

