import os, sys, re, time, textwrap, curses, threading, importlib.util, functools, sounddevice as sd, json, subprocess
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
stop_event = threading.Event()

# Utils - because who doesn't love utilities?
def load_module(name, path):
    """Load a fucking module like a boss"""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

class SilentStdErr:
    """Shut the fuck up, stderr!"""
    def __enter__(self):
        self.fd = os.dup(2)
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.devnull, 2)
    def __exit__(self, *a):
        os.dup2(self.fd, 2)
        os.close(self.devnull)
        os.close(self.fd)

# =========================
# Logo - look at this beautiful shit
# =========================
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
        print("\n".join(logo), "\nv 0.2.0\n")

# =========================
# Modules - the brain of this whole operation
# =========================
def load_whisper():
    """Load Whisper so we can actually hear what the fuck you're saying"""
    p = BASE / "stt" / "whisper-medium" / "whismedium.py"
    if not p.exists(): return None
    return load_module("whismedium", str(p)).VoiceListener()

def load_engine():
    """Choose your AI poison - the smart one or the other smart one"""
    if not CHOICE_FILE.exists():
        CHOICE_FILE.write_text("yi")  # Default to the good shit
    model_choice = CHOICE_FILE.read_text().strip().lower()
    if model_choice == "yi":
        path = BASE / "llm" / "yi-1.5-6b-chat-q4" / "yiusage.py"
        eng = load_module("yiusage", str(path))
    else:
        path = BASE / "llm" / "phi-3-mini" / "phi3usage.py"
        eng = load_module("phiusage", str(path))
    return eng

# =========================
# ALSA Mics - find something to hear your beautiful voice
# =========================
def list_all_mics():
    """List all microphones because apparently you have options"""
    devices = []
    try:
        for i, d in enumerate(sd.query_devices()):
            if d["max_input_channels"] > 0:
                devices.append(f"{i} - {d['name']}")
        if not devices:
            devices.append("default")  # Well fuck, no mics found
    except Exception as e:
        print("Error getting mics:", e)
        devices = ["default"]  # Plan B: use whatever the fuck is there
    return devices

# =========================
# Menu - where you make all the important life decisions
# =========================
def center_menu(stdscr, title, opts):
    """Center the menu because we're fancy like that"""
    curses.curs_set(0)  # Hide that ugly-ass cursor
    cur = 0
    while True:
        stdscr.clear(); gradient_logo(stdscr)
        h, w = stdscr.getmaxyx()
        stdscr.addstr(10, w // 2 - len(title)//2, title, curses.A_BOLD | curses.color_pair(6))
        for i, o in enumerate(opts):
            y = 12 + i; x = w // 2 - len(o)//2
            if i == cur:
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(y, x - 2, f"> {o} <")  # Look at me, I'm selected!
                stdscr.attroff(curses.color_pair(3))
            else:
                stdscr.addstr(y, x, o)
        stdscr.refresh()
        key = stdscr.getch()
        if key in [curses.KEY_UP, ord("k")]: cur = (cur - 1) % len(opts)  # Move up, dumbass
        elif key in [curses.KEY_DOWN, ord("j")]: cur = (cur + 1) % len(opts)  # Move down, genius
        elif key in [10, 13]: return cur  # Finally made a decision!

# =========================
# Chat display - where the magic happens
# =========================
def refresh_chat(stdscr, msgs, inp, curx, scroll, auto_scroll=True):
    """Refresh the chat because things change, you know?"""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    LOGO_HEIGHT = 7
    x_offset = 3

    gradient_logo(stdscr)  # Show off that beautiful logo

    # Wrap messages so they don't go off the fucking screen
    wrapped_msgs = []
    total_height = 0
    for role, msg in msgs:
        color = curses.color_pair(3) if role == "you" else curses.color_pair(4)  # You get blue, AI gets cyan
        lines = textwrap.wrap(msg, w - 2*x_offset)
        wrapped_msgs.append((role, lines, color))
        total_height += len(lines) + 1

    # Handle scrolling because sometimes there's too much text
    visible_height = h - LOGO_HEIGHT - 5
    max_scroll = max(total_height - visible_height, 0)
    scroll = max_scroll if auto_scroll else min(max(scroll, 0), max_scroll)

    # Actually display the fucking messages
    y = LOGO_HEIGHT
    height_count = 0
    for role, lines, color in wrapped_msgs:
        for line in lines:
            if height_count >= scroll:
                if y < h - 5:
                    stdscr.addstr(y, x_offset, line[:w - 2*x_offset], color)
                    y += 1
            height_count += 1
        height_count += 1
        if y >= h - 5: break  # No more space, fuck it

    # Input box - where you type your brilliant thoughts
    wrapped_input = textwrap.wrap(inp, w - 2*x_offset)
    box_height = max(len(wrapped_input), 1) + 2
    input_y = h - box_height - 2

    stdscr.addstr(input_y - 1, w // 2 - 2, " you ", curses.color_pair(6))  # That's you, buddy!
    stdscr.addstr(input_y, 1, "╭" + "─" * (w - 4) + "╮")

    if not inp.strip():
        # Show placeholder when you're not typing anything useful
        placeholder = "> write /help for commands list"
        stdscr.addstr(input_y + 1, 1, f"│ {' ' * (w - 4)}│")
        stdscr.addstr(input_y + 1, x_offset, placeholder[:w - 2*x_offset], curses.color_pair(1) | curses.A_DIM)
        stdscr.addstr(input_y + 2, 1, "╰" + "─" * (w - 4) + "╯")
    else:
        # Show what you're actually typing
        for i, line in enumerate(wrapped_input or [" "]):
            stdscr.addstr(input_y + 1 + i, 1, f"│ {line.ljust(w - 4)}│")
        stdscr.addstr(input_y + box_height - 1, 1, "╰" + "─" * (w - 4) + "╯")

    # Cursor positioning - make sure it's in the right fucking place
    cursor_y = input_y + 1 + (len(wrapped_input) - 1)
    cursor_x = len(wrapped_input[-1]) + 2 if wrapped_input else 2
    try: stdscr.move(cursor_y, min(cursor_x, w - 3))
    except curses.error: stdscr.move(h - 2, 2)  # Fuck it, just put it somewhere

    # Show who's talking with fancy indicators
    for i, (role, lines, color) in enumerate(wrapped_msgs[-5:]):
        if role == "system": continue  # Skip system messages, they're boring
        if lines:
            indicator = "🫵" if role == "you" else "🤖"  # Pointing finger for you, robot for AI
            try: stdscr.addstr(LOGO_HEIGHT + i, 0, indicator, color)
            except curses.error: pass  # If it doesn't fit, fuck it

    # Highlight the last AI message because it's probably important
    if msgs and msgs[-1][0] == "ai":
        last_msg_lines = textwrap.wrap(msgs[-1][1], w - 2*x_offset)
        if last_msg_lines:
            try: stdscr.addstr(y - 1, x_offset, last_msg_lines[-1][:w - 2*x_offset], curses.color_pair(5) | curses.A_BOLD)
            except curses.error: pass

    # Progress bar for when AI is thinking hard
    if auto_scroll and msgs and msgs[-1][0] == "ai":
        try:
            progress_bar_y = input_y - 2
            bar_length = w - 4
            progress = min(len(msgs[-1][1]) / 1000, 1.0)  # Don't go over 100%, you overachiever
            filled = int(bar_length * progress)
            stdscr.addstr(progress_bar_y, 2, "█" * filled + "-" * (bar_length - filled), curses.color_pair(2))
        except curses.error: pass  # Progress bar failed, who gives a shit

    # Dim the logo area because it's not that important
    for i in range(LOGO_HEIGHT):
        try: stdscr.chgat(i, 0, w, curses.A_DIM)
        except curses.error: pass

    # Draw some fucking borders because we're professional
    try:
        for y_frame in range(LOGO_HEIGHT, h - box_height - 2):
            stdscr.addstr(y_frame, 0, "│")
            stdscr.addstr(y_frame, w - 1, "│")
        stdscr.addstr(LOGO_HEIGHT, 0, "╭" + "─" * (w - 2) + "╮")
        stdscr.addstr(h - box_height - 2, 0, "╰" + "─" * (w - 2) + "╯")
    except curses.error: pass  # Borders didn't work, whatever

    # Status bar - because you need to know what the fuck is going on
    try:
        status = f"Msgs: {len(msgs)} | Scroll: {scroll}/{max_scroll}"
        stdscr.addstr(h - 1, 2, status[:w-4], curses.color_pair(6))
    except curses.error: pass  # Status failed, nobody will notice

    stdscr.refresh()
    return scroll

# =========================
# Streaming generation with TTS - where AI talks back!
# =========================
def stream_with_tts(prompt, eng, stdscr, msgs):
    """Stream AI response with TTS because reading is for losers"""
    global tts_enabled
    msgs.append(("ai", ""))  # Add empty AI message to fill later
    refresh_chat(stdscr, msgs, "", 0, 0)

    buffer = ""
    pat = re.compile(r"[^.!?]+[.!?]")  # Find sentences to speak

    def speak(s):
        """Speak the sentence if TTS is enabled"""
        if tts_enabled:
            threading.Thread(target=lambda: speech_queue.put(s.strip()), daemon=True).start()

    # Get the AI to actually generate some text
    if hasattr(eng, "ask_stream"):
        stream = eng.ask_stream(prompt, max_tokens=300, temperature=0.7)  # Ask the AI nicely
    else:
        stream = eng.llm.create_chat_completion(
            messages=eng.messages + [{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
            stream=True  # Stream that shit!
        )

    reply = ""
    for chunk in stream:
        token = chunk["choices"][0]["delta"]["content"] if "choices" in chunk else chunk
        reply += token
        msgs[-1] = ("ai", msgs[-1][1] + token)  # Update the message in real-time
        refresh_chat(stdscr, msgs, "", 0, 0)

        # Speak sentences as they complete
        buffer += token
        while m := pat.match(buffer):
            speak(m.group().strip())  # Say it out loud, motherfucker!
            buffer = buffer[len(m.group()):].lstrip()

    # Remember this conversation for later
    if hasattr(eng, "messages"):
        eng.messages.append({"role": "user", "content": prompt})
        eng.messages.append({"role": "assistant", "content": reply})

# =========================
# Context memory - because AI has goldfish memory
# =========================
def save_memory(msgs):
    """Save this glorious conversation so we don't forget it"""
    data = [m for m in msgs if m[0] in ("you", "ai")]  # Only save user and AI messages
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_memory():
    """Load previous conversation because starting over is for quitters"""
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    return []  # No memory? Must be your first time

def clear_memory():
    """Forget everything and start fresh - the digital equivalent of getting blackout drunk"""
    if MEMORY_FILE.exists():
        MEMORY_FILE.unlink()

# =========================
# Background listening thread - always listening, like the NSA
# =========================
def voice_listener_thread(listener, msgs, stdscr, eng):
    """Listen for voice input in the background because multitasking is cool"""
    while not stop_event.is_set():
        try:
            text = listener.listen_once()
            if text:
                msgs.append(("you", text))  # You said something!
                stream_with_tts(text, eng, stdscr, msgs)  # Let AI respond
        except Exception as e:
            msgs.append(("system", f"Voice stream error: {e}"))  # Oops, something broke
        time.sleep(0.1)  # Don't use 100% CPU, you greedy bastard

# =========================
# Main loop - where everything comes together in a beautiful mess
# =========================
def main(stdscr):
    """The main event - where the magic happens and bugs are born"""
    global tts_enabled
    curses.start_color(); curses.use_default_colors()
    # Set up colors because black and white is for cavemen
    colors = [213, 177, 81, 123, curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_YELLOW]
    for i, c in enumerate(colors, 1): curses.init_pair(i, c, -1)

    # Check if we have previous config or need to start from scratch
    if all(f.exists() for f in [MIC_FILE, INPUT_FILE, CHOICE_FILE]):
        ans = center_menu(stdscr, "📦 Use previous config?", ["✅ Yes", "🔧 Choose new"])
        if ans == 1:  # User wants new config, fuck the old one
            for f in [MIC_FILE, INPUT_FILE, CHOICE_FILE]:
                try: f.unlink()  # Delete that shit
                except: pass  # If it fails, whatever

    # Microphone selection - pick something that works
    devices = list_all_mics()
    if not devices: devices = ["default"]  # Well fuck, no mics
    if MIC_FILE.exists(): mic = MIC_FILE.read_text().strip()  # Use saved mic
    else:
        mic = devices[center_menu(stdscr, "🎙 Choose microphone", devices)]  # Let user choose
        MIC_FILE.write_text(mic)  # Remember this choice
    sd.default.device = (mic, None)  # Set the fucking microphone

    # Input mode selection - talk or type, your choice
    modes = ["VOICE", "MANUAL"]
    if INPUT_FILE.exists(): mode = INPUT_FILE.read_text().strip().upper()  # Use saved mode
    else:
        mode = modes[center_menu(stdscr, "🎚 Input mode", modes)]  # Let user choose
        INPUT_FILE.write_text(mode.lower())  # Remember this too

    # Model selection - choose your AI brain
    models = ["yi", "phi"]
    if CHOICE_FILE.exists(): model = CHOICE_FILE.read_text().strip()  # Use saved model
    else:
        model = models[center_menu(stdscr, "🤖 Choose LLM", models)]  # Let user pick their poison
        CHOICE_FILE.write_text(model)  # Save for next time

    # Load all the fucking components
    eng = load_engine(); listener = load_whisper(); start_tts()
    msgs = [("system", f"🎙 Microphone: {mic} | Mode: {mode} | Model: {model}")] + load_memory()
    inp = ""; curx = 0; scroll = 0

    # Start background thread for VOICE mode if we have a listener
    if mode == "VOICE" and listener:
        threading.Thread(target=voice_listener_thread, args=(listener, msgs, stdscr, eng), daemon=True).start()

    help_text = (
        "🧠 Commands:\n"
        "/save - save memory\n"
        "/load - load memory\n"
        "/clear - clear memory\n"
        "/help - show commands\n"
        "/mute - turn off voice\n"
        "/voice - voice mode\n"
        "/manual - manual mode\n"
        "exit - exit"
    )

    # Main event loop - where you spend most of your time
    while True:
        scroll = refresh_chat(stdscr, msgs, inp, curx, scroll)
        key = stdscr.get_wch()
        if key in ("\n", "\r"):  # Enter pressed - do something!
            txt = inp.strip()
            if not txt: continue  # Empty message, fuck that
            if txt.lower() in ["exit", "quit"]: break  # Get me out of here!

            if txt.startswith("/"):  # It's a command, do command things
                cmd = txt.lower()
                if cmd == "/save":
                    save_memory(msgs)
                    msgs.append(("system", "💾 Memory saved"))  # Good job, you saved something
                elif cmd == "/load":
                    msgs = [("system", "🔁 Memory loaded")] + load_memory()  # Load that shit
                elif cmd == "/clear":
                    clear_memory()
                    msgs.append(("system", "🧹 Memory cleared"))  # Out with the old!
                elif cmd == "/help":
                    msgs.append(("system", help_text))  # Show the fucking help
                elif cmd == "/mute":
                    tts_enabled = not tts_enabled  # Toggle that voice
                    msgs.append(("system", f"🔇 Voice {'off' if not tts_enabled else 'on'}"))  # Tell user what happened
                elif cmd in ["/voice", "/manual"]:
                    mode = cmd.strip("/").upper()  # Switch modes
                    INPUT_FILE.write_text(mode.lower())  # Save the new mode
                    msgs.append(("system", f"🔄 Switched to {mode}"))  # Inform the user
                else:
                    msgs.append(("system", f"❓ Unknown command: {cmd}"))  # You typed what now?
                inp = ""; continue

            # Handle actual user input
            if not txt and mode == "VOICE" and listener:
                msgs.append(("system", "🎧 Listening..."))  # Get ready to listen
                refresh_chat(stdscr, msgs, "", 0, scroll)
                prompt = listener.listen_once() or "(silence)"  # Listen or get silence
                msgs.append(("you", prompt))  # Add what you said
            else:
                prompt = txt  # Use typed text
                msgs.append(("you", prompt))  # Add to messages
            
            # Let AI respond to your brilliant input
            stream_with_tts(prompt, eng, stdscr, msgs)
            inp = ""; curx = 0  # Clear input for next message
        elif key in ("\b", "\x7f", curses.KEY_BACKSPACE) and curx>0:  # Backspace - delete that typo
            inp = inp[:curx-1] + inp[curx:]; curx -= 1
        elif key == curses.KEY_LEFT and curx>0: curx -= 1  # Move left
        elif key == curses.KEY_RIGHT and curx<len(inp): curx += 1  # Move right
        elif key == curses.KEY_UP: scroll = min(scroll+1, len(msgs))  # Scroll up
        elif key == curses.KEY_DOWN: scroll = max(scroll-1, 0)  # Scroll down
        elif isinstance(key, str):  # Normal character input
            inp = inp[:curx] + key + inp[curx:]; curx += len(key)  # Add character and move cursor

if __name__ == "__main__":
    os.system("clear"); curses.wrapper(main)  # Clear screen and start the fucking show
