import os
import sys
import curses
import time
import textwrap
import importlib.util
import functools
import threading
from pathlib import Path
from tts.edgetts.edgetts import speech_queue, start_tts

print = functools.partial(print, flush=True)
sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")

# === COLORS ===
RESET = "\033[0m"
BOLD = "\033[1m"
WHITE = "\033[97m"
GRAY = "\033[90m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
PURPLE = "\033[38;5;177m"
PINK = "\033[38;5;213m"

def gradient_logo():
    logo_lines = [
        "██╗██╗      ██╗ █████╗ ██╗",
        "██║██║      ██║██╔══██╗██║",
        "██║██║      ██║███████║██║",
        "██║██║      ██║██╔══██║██║",
        "██║███████╗ ██║██║  ██║██║",
        "╚═╝╚══════╝ ╚═╝╚═╝  ╚═╝╚═╝",
    ]
    colors = [PINK, MAGENTA, PURPLE, BLUE, CYAN, WHITE]
    for i, line in enumerate(logo_lines):
        color = colors[i % len(colors)]
        print(f"{color}{line}{RESET}")
    print(f"{GRAY}                v 0.0.2{RESET}\n")

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

class SilentStdErr:
    def __enter__(self):
        self.stderr_fd = os.dup(2)
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.devnull, 2)
        return self
    def __exit__(self, *args):
        os.dup2(self.stderr_fd, 2)
        os.close(self.devnull)
        os.close(self.stderr_fd)

def refresh_chat(stdscr, messages, user_input, cursor_x):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    logo_y = 1
    logo_x = (width // 2) - 14
    gradient = [5, 13, 177, 213, 81, 123]
    logo_text = [
        "██╗██╗      ██╗ █████╗ ██╗",
        "██║██║      ██║██╔══██╗██║",
        "██║██║      ██║███████║██║",
        "██║██║      ██║██╔══██║██║",
        "██║███████╗ ██║██║  ██║██║",
        "╚═╝╚══════╝ ╚═╝╚═╝  ╚═╝╚═╝",
    ]
    for i, line in enumerate(logo_text):
        stdscr.attron(curses.color_pair(i % len(gradient) + 1))
        stdscr.addstr(logo_y + i, logo_x, line)
        stdscr.attroff(curses.color_pair(i % len(gradient) + 1))
    stdscr.addstr(logo_y + len(logo_text), logo_x + 10, "v 0.0.2", curses.color_pair(8))

    y = logo_y + len(logo_text) + 3
    for role, msg in messages[-(height - 10):]:
        color = curses.color_pair(3) if role == "you" else curses.color_pair(4)
        wrapped = textwrap.wrap(msg, width - 6)
        for line in wrapped:
            if y < height - 7:
                stdscr.addstr(y, 2, line, color)
                y += 1
        y += 1

    # Input box
    box_w = width - 10
    box_x = (width - box_w) // 2
    stdscr.addstr(height - 5, box_x + (box_w // 2) - 2, " you ", curses.color_pair(6) | curses.A_BOLD)
    stdscr.addstr(height - 4, box_x, "╭" + "─" * (box_w - 2) + "╮")
    stdscr.addstr(height - 3, box_x, f"│ {user_input[:box_w - 4].ljust(box_w - 4)} │")
    stdscr.addstr(height - 2, box_x, "╰" + "─" * (box_w - 2) + "╯")

    # Курсор
    stdscr.move(height - 3, box_x + 2 + cursor_x)

    stdscr.refresh()

def stream_with_tts(prompt, engine, stdscr, messages):
    sentence_buffer = ""
    first_sentence_done = False
    accumulated_reply = ""

    messages.append(("system", "🤖 ИИ думает..."))
    refresh_chat(stdscr, messages, "", 0)

    with SilentStdErr():
        for token in engine.ask_stream(prompt, max_tokens=200, temperature=0.7):
            accumulated_reply += token
            refresh_chat(stdscr, messages[:-1] + [("ai", accumulated_reply)], "", 0)
            if not first_sentence_done and any(p in accumulated_reply for p in [".", "!", "?"]):
                first_sentence_done = True
                threading.Thread(target=lambda s=accumulated_reply: speech_queue.put(s)).start()

    threading.Thread(target=lambda s=accumulated_reply: speech_queue.put(s)).start()
    messages[-1] = ("ai", accumulated_reply)
    refresh_chat(stdscr, messages, "", 0)

# === Main loop ===
def main(stdscr):
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, 213, -1)
    curses.init_pair(2, 177, -1)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, curses.COLOR_WHITE, -1)
    curses.init_pair(5, 81, -1)
    curses.init_pair(6, curses.COLOR_BLUE, -1)
    curses.init_pair(7, curses.COLOR_MAGENTA, -1)
    curses.init_pair(8, curses.COLOR_YELLOW, -1)

    BASE = Path(__file__).resolve().parent
    CHOICE_FILE = BASE / "model_choice.txt"

    if CHOICE_FILE.exists():
        model_choice = CHOICE_FILE.read_text().strip()
    else:
        model_choice = "phi"
        CHOICE_FILE.write_text(model_choice)

    if model_choice == "yi":
        engine = load_module("yiusage", str(BASE / "llm" / "yi-1.5-6b-chat-q4" / "yiusage.py"))
    else:
        engine = load_module("phiusage", str(BASE / "llm" / "phi-3-mini" / "phiusage.py"))

    start_tts()

    messages = []
    user_input = ""
    cursor_x = 0

    curses.curs_set(1)
    stdscr.keypad(True)

    while True:
        refresh_chat(stdscr, messages, user_input, cursor_x)
        key = stdscr.get_wch()

        if isinstance(key, str) and key in ("\n", "\r"):
            text = user_input.strip()
            if text.lower() in ["exit", "quit", "выход"]:
                break
            if text:
                messages.append(("you", text))
                refresh_chat(stdscr, messages, "", 0)
                stream_with_tts(text, engine, stdscr, messages)
            user_input = ""
            cursor_x = 0

        elif key == "\x1b":
            break

        elif key in ("\b", "\x7f", curses.KEY_BACKSPACE):
            if cursor_x > 0:
                user_input = user_input[:cursor_x - 1] + user_input[cursor_x:]
                cursor_x -= 1

        elif key == curses.KEY_LEFT and cursor_x > 0:
            cursor_x -= 1
        elif key == curses.KEY_RIGHT and cursor_x < len(user_input):
            cursor_x += 1
        elif key == curses.KEY_DC and cursor_x < len(user_input):
            user_input = user_input[:cursor_x] + user_input[cursor_x + 1:]
        elif isinstance(key, str) and key.isprintable():
            user_input = user_input[:cursor_x] + key + user_input[cursor_x:]
            cursor_x += 1

if __name__ == "__main__":
    os.system("clear")
    gradient_logo()
    time.sleep(0.4)
    curses.wrapper(main)

