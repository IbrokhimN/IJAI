import os
import sys
import functools
import importlib.util
import threading
from pathlib import Path
from tts.edgetts.edgetts import speech_queue, start_tts

print = functools.partial(print, flush=True)

def load_module(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

class SilentStdErr:
    """Временно заглушил stderr."""
    def __enter__(self):
        self.stderr_fd = os.dup(2)
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.devnull, 2)
        return self
    def __exit__(self, *a):
        os.dup2(self.stderr_fd, 2)
        os.close(self.devnull)
        os.close(self.stderr_fd)
BASE = Path(__file__).resolve().parent
CHOICE_FILE = BASE / "model_choice.txt"

if CHOICE_FILE.exists():
    model_choice = CHOICE_FILE.read_text().strip()
    print(f"► Loaded previous choice: {model_choice}")
else:
    while True:
        choice = input("► Pick a model ('yi' or 'phi'): ").strip().lower()
        if choice in ["yi", "phi"]:
            model_choice = choice
            CHOICE_FILE.write_text(model_choice)
            break
        print("⬢ Invalid choice. Type 'yi' or 'phi'.")

if model_choice == "yi":
    module_path = BASE / "llm/yi-1.5-6b-chat-q4/yiusage.py"
    engine = load_module("yiusage", str(module_path))
    print("★ Yi model loaded. Start chatting!")
else:
    module_path = BASE / "llm/phi-3-mini/phiusage.py"
    engine = load_module("phiusage", str(module_path))
    print("★ Phi-3-mini model loaded. Start chatting!")

start_tts()
print("► Type 'exit' or Ctrl+C to quit.")

def stream_with_tts(prompt):
    print("\nBot:", end=" ", flush=True)
    sentence_buffer = ""
    first_sentence_done = False
    accumulated_reply = ""

    with SilentStdErr():
        for token in engine.ask_stream(prompt, max_tokens=200, temperature=0.7):
            print(token, end="", flush=True)
            sentence_buffer += token
            accumulated_reply += token

            # первое предложение
            if not first_sentence_done and any(p in sentence_buffer for p in [".", "!", "?"]):
                first_sentence_done = True
                first_sentence_to_say = sentence_buffer.strip()
                first_sentence_len = len(first_sentence_to_say)
                threading.Thread(target=lambda s=first_sentence_to_say: speech_queue.put(s), args=(first_sentence_to_say,)).start()
                sentence_buffer = ""  # очистил буфер для остального

    rest = accumulated_reply[first_sentence_len:].strip() if first_sentence_done else accumulated_reply.strip()
    if rest:
        threading.Thread(target=lambda s=rest: speech_queue.put(s), args=(rest,)).start()

while True:
    try:
        prompt = input("\nYou: ")
        if prompt.strip().lower() in ["exit", "quit"]:
            break
        stream_with_tts(prompt)
    except KeyboardInterrupt:
        print("\nExiting chat...")
        break

speech_queue.put(None)

