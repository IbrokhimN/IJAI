import os, sys, re, time, textwrap, curses, threading, importlib.util, functools, sounddevice as sd, json
from pathlib import Path
from tts.edgetts.edgetts import speech_queue, start_tts

print = functools.partial(print, flush=True)
sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent
CHOICE_FILE = BASE / "model_choice.txt"
INPUT_FILE = BASE / "input_mode.txt"
MIC_FILE = BASE / "mic_choice.txt"
MEMORY_FILE = BASE / "memory.json"

tts_enabled = True  

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

class SilentStdErr:
    def __enter__(self):
        self.fd = os.dup(2)
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.devnull, 2)
    def __exit__(self, *a):
        os.dup2(self.fd, 2)
        os.close(self.devnull)
        os.close(self.fd)
# my own ahh logo
def gradient_logo(stdscr=None):
    logo = [
        "██╗     ██╗ █████╗ ██╗",
        "██║     ██║██╔══██╗██║",
        "██║     ██║███████║██║",
        "██║██   ██║██╔══██║██║",
        "██║╚█████╔╝██║  ██║██║",
        "╚═╝ ╚════╝ ╚═╝  ╚═╝╚═╝"
    ]
    if stdscr:
        h, w = stdscr.getmaxyx()
        for i, line in enumerate(logo):
            stdscr.attron(curses.color_pair(i + 1))
            stdscr.addstr(2 + i, w // 2 - 14, line)
            stdscr.attroff(curses.color_pair(i + 1))
        stdscr.addstr(2 + len(logo), w // 2 - 4, "v 0.2.0", curses.color_pair(6))
    else:
        print("\n".join(logo), "\nv 0.5.0\n")

# modules?
def load_whisper():
    p = BASE / "stt" / "whisper-medium" / "whismedium.py"
    if not p.exists(): return None
    return load_module("whismedium", str(p)).VoiceListener()

def load_engine():
    if not CHOICE_FILE.exists():
        CHOICE_FILE.write_text("yi")
    model_choice = CHOICE_FILE.read_text().strip().lower()
    if model_choice == "yi":
        path = BASE / "llm" / "yi-1.5-6b-chat-q4" / "yiusage.py"
        eng = load_module("yiusage", str(path))
    else:
        path = BASE / "llm" / "phi-3-mini" / "phiusage.py"
        eng = load_module("phiusage", str(path))
    return eng

# im sorry for what im gonna do rn
def center_menu(stdscr, title, opts):
    curses.curs_set(0)
    cur = 0
    while True:
        stdscr.clear(); gradient_logo(stdscr)
        h, w = stdscr.getmaxyx()
        stdscr.addstr(10, w // 2 - len(title)//2, title, curses.A_BOLD | curses.color_pair(6))
        for i, o in enumerate(opts):
            y = 12 + i; x = w // 2 - len(o)//2
            if i == cur:
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(y, x - 2, f"> {o} <")
                stdscr.attroff(curses.color_pair(3))
            else:
                stdscr.addstr(y, x, o)
        stdscr.refresh()
        key = stdscr.getch()
        if key in [curses.KEY_UP, ord("k")]: cur = (cur - 1) % len(opts)
        elif key in [curses.KEY_DOWN, ord("j")]: cur = (cur + 1) % len(opts)
        elif key in [10, 13]: return cur

# out stuff
def refresh_chat(stdscr, msgs, inp, curx, scroll):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    gradient_logo(stdscr)

    y = 9 - scroll
    visible_height = h - 12
    msgs_to_show = msgs[-visible_height:]

    for role, msg in msgs_to_show:
        color = curses.color_pair(3) if role == "you" else curses.color_pair(4)
        wrapped = textwrap.wrap(msg, w - 6)
        for line in wrapped:
            if 0 < y < h - 6:
                stdscr.addstr(y, 3, line[:w-6], color)
            y += 1
        y += 1

    wrapped_input = textwrap.wrap(inp, w - 8)
    box_height = len(wrapped_input) + 2
    input_y = h - box_height - 2
    stdscr.addstr(input_y - 1, w // 2 - 2, " you ", curses.color_pair(6))
    stdscr.addstr(input_y, 1, "╭" + "─" * (w - 4) + "╮")
    for i, line in enumerate(wrapped_input or [" "]):
        stdscr.addstr(input_y + 1 + i, 1, f"│ {line.ljust(w - 6)}│")
    stdscr.addstr(input_y + box_height - 1, 1, "╰" + "─" * (w - 4) + "╯")

    cursor_y = input_y + 1 + (len(wrapped_input) - 1)
    cursor_x = len(wrapped_input[-1]) + 2 if wrapped_input else 2
    try:
        stdscr.move(cursor_y, min(cursor_x, w - 3))
    except curses.error:
        stdscr.move(h - 2, 2)
    stdscr.refresh()

# live tts
def stream_with_tts(prompt, eng, stdscr, msgs):
    global tts_enabled
    buffer = ""
    full = ""
    pat = re.compile(r"[^.!?]+[.!?]")
    msgs.append(("ai", "🤖 Думаю..."))
    refresh_chat(stdscr, msgs, "", 0, 0)

    def speak(s):
        if tts_enabled:
            threading.Thread(target=lambda: speech_queue.put(s.strip()), daemon=True).start()

    with SilentStdErr():
        for t in eng.ask_stream(prompt, max_tokens=300, temperature=0.7):
            full += t; buffer += t
            refresh_chat(stdscr, msgs[:-1] + [("ai", full)], "", 0, 0)
            while m := pat.match(buffer):
                s = m.group().strip()
                speak(s)
                buffer = buffer[len(s):].lstrip()

    if buffer.strip(): speak(buffer.strip())
    msgs[-1] = ("ai", full)
    refresh_chat(stdscr, msgs, "", 0, 0)

def save_memory(msgs):
    data = [m for m in msgs if m[0] in ("you", "ai")]
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_memory():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    return []

def clear_memory():
    if MEMORY_FILE.exists():
        MEMORY_FILE.unlink()

def main(stdscr):
    global tts_enabled
    curses.start_color(); curses.use_default_colors()
    colors = [213, 177, 81, 123, curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_YELLOW]
    for i, c in enumerate(colors, 1): curses.init_pair(i, c, -1)

    if all(f.exists() for f in [MIC_FILE, INPUT_FILE, CHOICE_FILE]):
        ans = center_menu(stdscr, "📦 Использовать прошлый конфиг?", ["✅ Да", "🔧 Выбрать новый"])
        if ans == 1:
            for f in [MIC_FILE, INPUT_FILE, CHOICE_FILE]:
                try: f.unlink()
                except: pass

    devices = [d["name"] for d in sd.query_devices() if d["max_input_channels"] > 0]
    if MIC_FILE.exists(): mic = MIC_FILE.read_text().strip()
    else:
        mic = devices[center_menu(stdscr, "🎙 Выберите микрофон", devices)]
        MIC_FILE.write_text(mic)
    sd.default.device = (mic, None)

    modes = ["VOICE", "MANUAL"]
    if INPUT_FILE.exists(): mode = INPUT_FILE.read_text().strip().upper()
    else:
        mode = modes[center_menu(stdscr, "🎚 Режим ввода", modes)]
        INPUT_FILE.write_text(mode.lower())

    models = ["yi", "phi"]
    if CHOICE_FILE.exists(): model = CHOICE_FILE.read_text().strip()
    else:
        model = models[center_menu(stdscr, "🤖 Выберите LLM", models)]
        CHOICE_FILE.write_text(model)

    eng = load_engine(); listener = load_whisper(); start_tts()

    msgs = [("system", f"🎙 Микрофон: {mic} | Режим: {mode} | Модель: {model}")]
    msgs += load_memory()
    inp = ""; curx = 0; scroll = 0

    help_text = (
        "🧠 Команды:\n"
        "/save — сохранить память\n"
        "/load — загрузить память\n"
        "/clear — очистить память\n"
        "/help — показать команды\n"
        "/mute — выключить озвучку\n"
        "/voice — голосовой режим\n"
        "/manual — ручной режим\n"
        "exit — выйти"
    )

    while True:
        refresh_chat(stdscr, msgs, inp, curx, scroll)
        key = stdscr.get_wch()
        if key in ("\n", "\r"):
            txt = inp.strip()
            if not txt: continue
            if txt.lower() in ["exit", "quit"]: break

            # === Команды ===
            if txt.startswith("/"):
                cmd = txt.lower()
                if cmd == "/save":
                    save_memory(msgs)
                    msgs.append(("system", "💾 Память сохранена."))
                elif cmd == "/load":
                    msgs = [("system", "🔁 Память загружена.")] + load_memory()
                elif cmd == "/clear":
                    clear_memory()
                    msgs.append(("system", "🧹 Память очищена."))
                elif cmd == "/help":
                    msgs.append(("system", help_text))
                elif cmd == "/mute":
                    tts_enabled = not tts_enabled
                    msgs.append(("system", f"🔇 Озвучка {'выключена' if not tts_enabled else 'включена'}"))
                elif cmd in ["/voice", "/manual"]:
                    mode = cmd.strip("/").upper()
                    INPUT_FILE.write_text(mode.lower())
                    msgs.append(("system", f"🔄 Переключено на {mode}"))
                else:
                    msgs.append(("system", f"❓ Неизвестная команда: {cmd}"))
                inp = ""; continue

            # === Ввод ===
            if not txt and mode == "VOICE" and listener:
                msgs.append(("system", "🎧 Слушаю..."))
                refresh_chat(stdscr, msgs, "", 0, scroll)
                prompt = listener.listen_once() or "(тишина)"
                msgs.append(("you", prompt))
            else:
                prompt = txt
                msgs.append(("you", prompt))
            stream_with_tts(prompt, eng, stdscr, msgs)
            inp = ""; curx = 0
        elif key in ("\b", "\x7f", curses.KEY_BACKSPACE) and curx>0:
            inp = inp[:curx-1] + inp[curx:]; curx -= 1
        elif key == curses.KEY_LEFT and curx>0: curx -= 1
        elif key == curses.KEY_RIGHT and curx<len(inp): curx += 1
        elif key == curses.KEY_UP: scroll = min(scroll+1, len(msgs))
        elif key == curses.KEY_DOWN: scroll = max(scroll-1, 0)
        elif isinstance(key, str) and key.isprintable():
            inp = inp[:curx] + key + inp[curx:]; curx += 1

if __name__ == "__main__":
    os.system("clear"); curses.wrapper(main)

