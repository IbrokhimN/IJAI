#!/usr/bin/env python3
import os
import sys
import time
import termios
import tty
import shutil
import subprocess
import textwrap
import json

# ===============================
#  CATPPUCCIN + EXTRA THEMES
# ===============================
THEMES = {
    "Mocha": {
        "accent": "\033[38;2;245;194;231m",
        "border": "─",
        "dot": "● ",
        "bg": (24, 24, 37),
    },
    "Macchiato": {
        "accent": "\033[38;2;244;219;214m",
        "border": "─",
        "dot": "◆ ",
        "bg": (30, 32, 48),
    },
    "Frappe": {
        "accent": "\033[38;2;202;158;230m",
        "border": "─",
        "dot": "◉ ",
        "bg": (48, 52, 70),
    },
    "Latte": {
        "accent": "\033[38;2;220;138;120m",
        "border": "─",
        "dot": "● ",
        "bg": (239, 241, 245),
    },
    "DoomDark": {
        "accent": "\033[38;2;255;85;85m",
        "border": "─",
        "dot": "⛧ ",
        "bg": (18, 18, 18),
    },
    "Sandstorm": {
        "accent": "\033[38;2;194;178;128m",
        "border": "─",
        "dot": "○ ",
        "bg": (242, 224, 169),
    },
    "Forest": {
        "accent": "\033[38;2;120;220;120m",
        "border": "─",
        "dot": "♣ ",
        "bg": (15, 30, 20),
    },
    "Midnight": {
        "accent": "\033[38;2;102;252;241m",
        "border": "─",
        "dot": "★ ",
        "bg": (11, 12, 16),
    },
    "Neon": {
        "accent": "\033[38;2;57;255;20m",
        "border": "─",
        "dot": "✦ ",
        "bg": (10, 10, 20),
    },
    "Matrix": {
        "accent": "\033[38;2;0;255;70m",
        "border": "─",
        "dot": "▓ ",
        "bg": (0, 0, 0),
    },
}

# ===============================
#  CONFIG SAVE / LOAD
# ===============================
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "theme.json")


def save_theme(theme_name):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"theme": theme_name}, f)
    except Exception as e:
        print(f"⚠ Ошибка при сохранении темы: {e}")


def load_theme():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                theme = data.get("theme")
                if theme in THEMES:
                    return theme
        except Exception:
            pass
    return "Mocha"  # по умолчанию


# ===============================
#  GLOBALS
# ===============================
current_theme = load_theme()
animation_speed = 0.02

# ===============================
#  UTILS
# ===============================
def clear():
    os.system('clear' if os.name == 'posix' else 'cls')


def get_terminal_size():
    size = shutil.get_terminal_size()
    return size.columns, size.lines


def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == "\x1b":
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def set_terminal_bg(rgb):
    r, g, b = rgb
    sys.stdout.write(f"\033]11;rgb:{r:02x}/{g:02x}/{b:02x}\033\\")
    sys.stdout.flush()


def reset_terminal_bg():
    sys.stdout.write("\033]111;\033\\")
    sys.stdout.flush()


def reset_colors():
    sys.stdout.write("\033[0m")
    sys.stdout.flush()


# ===============================
#  DRAW WINDOW
# ===============================
def draw_window(title, content_lines=None, selected_index=None, menu_items=None, scroll_offset=0):
    cols, rows = get_terminal_size()
    margin = 1
    theme = THEMES[current_theme]
    inner_width = max(20, cols - margin * 2 - 2)
    inner_height = max(6, rows - 6)

    set_terminal_bg(theme["bg"])
    clear()

    print("\n" * margin, end="")
    print(" " * margin + "╭" + theme["border"] * inner_width + "╮")
    print(" " * margin + "│  " + theme["accent"] + theme["dot"] * 3 + "\033[0m" + " " * (inner_width - 5) + "│")
    print(" " * margin + "│" + title.center(inner_width) + "│")
    print(" " * margin + "├" + theme["border"] * inner_width + "┤")

    content_lines = content_lines or []
    menu_items = menu_items or []

    wrapped_content = []
    for line in content_lines:
        if not line.strip():
            wrapped_content.append("")
        else:
            wrapped_content.extend(textwrap.wrap(line, width=inner_width - 2))

    visible_lines = inner_height - len(menu_items) - 6
    total_lines = len(wrapped_content)
    slice_start = max(0, scroll_offset)
    slice_end = min(total_lines, slice_start + visible_lines)
    visible_content = wrapped_content[slice_start:slice_end]

    for line in visible_content:
        print(" " * margin + "│" + line.center(inner_width) + "│")
    for _ in range(visible_lines - len(visible_content)):
        print(" " * margin + "│" + " " * inner_width + "│")

    if menu_items:
        print(" " * margin + "├" + theme["border"] * inner_width + "┤")
        for i, item in enumerate(menu_items):
            prefix = "➤ " if i == selected_index else "  "
            style = theme["accent"] + item + "\033[0m" if i == selected_index else item
            line = (prefix + style).center(inner_width)
            print(" " * margin + "│" + line + "│")

    print(" " * margin + "╰" + theme["border"] * inner_width + "╯")
    reset_colors()


# ===============================
#  SECTIONS
# ===============================
def start_section():
    theme = THEMES[current_theme]
    lines = [
        "Initializing IJAI core...",
        "Verifying model files...",
        "Loading models from models/ ...",
        "Spawning neural processes...",
        "Bringing core online..."
    ]
    clear()
    for ln in lines:
        print(theme["accent"] + ln + "\033[0m")
        time.sleep(max(0.01, animation_speed * 2))
    models_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "bunch.py"))
    if not os.path.exists(models_path):
        print("\n\033[91mError: file not found:\033[0m", models_path)
        input("\nPress Enter to return...")
        return
    print("\n" + theme["accent"] + "Launching module: " + models_path + "\033[0m")
    try:
        ret = subprocess.run([sys.executable, models_path])
        print("\n" + theme["accent"] + f"Process finished (code {ret.returncode})." + "\033[0m")
    except Exception as e:
        print("\n\033[91mFailed to launch module:\033[0m", e)
    input("\nPress Enter to return...")


def settings_menu():
    global animation_speed
    options = ["Animation Speed: Slow", "Animation Speed: Medium", "Animation Speed: Fast", "Back"]
    selected = 0
    while True:
        draw_window("⚙ SETTINGS ⚙", ["Adjust animation speed"], selected, options)
        key = get_key()
        if key == "\x1b[A": selected = (selected - 1) % len(options)
        elif key == "\x1b[B": selected = (selected + 1) % len(options)
        elif key in ("\n", "\r"):
            choice = options[selected]
            if "Slow" in choice: animation_speed = 0.08
            elif "Medium" in choice: animation_speed = 0.03
            elif "Fast" in choice: animation_speed = 0.01
            elif choice == "Back": return


def appearance_menu():
    global current_theme
    themes = list(THEMES.keys()) + ["Back"]
    selected = list(THEMES.keys()).index(current_theme) if current_theme in THEMES else 0
    while True:
        draw_window("APPEARANCE", ["Select theme"], selected, themes)
        key = get_key()
        if key == "\x1b[A": selected = (selected - 1) % len(themes)
        elif key == "\x1b[B": selected = (selected + 1) % len(themes)
        elif key in ("\n", "\r"):
            if themes[selected] == "Back":
                return
            current_theme = themes[selected]
            save_theme(current_theme)
            set_terminal_bg(THEMES[current_theme]["bg"])
            draw_window("APPEARANCE", [f"Theme set: {current_theme}"], None, [])
            time.sleep(0.4)


def about_screen():
    draw_window("ABOUT", [
        "IJAI CLI — A minimal AI launcher",
        "Now with extra themes and full-screen background!",
        "Made with love, style and caffeine",
        "See more on my github",
        "https://github.com/IbrokhimN/IJAI"
    ])
    input("\nPress Enter to return...")


# ===============================
#  MAIN
# ===============================
def colored_logo():
    return """\033[95m
▀████▀  ▀████▀     ██     ▀████▀
  ██      ██      ▄██▄      ██  
  ██      ██     ▄█▀██▄     ██  
  ██      ██    ▄█  ▀██     ██  
  ██      ██    ████████    ██  
  ██ ███  ██   █▀      ██   ██  
▄████▄█████  ▄███▄   ▄████▄████▄
\033[0m"""


def main():
    logo = colored_logo()
    title = "░▒▓ IJAI CLI ▓▒░"
    menu = ["Start", "Settings", "Appearance", "About", "Exit"]
    selected = 0

    try:
        set_terminal_bg(THEMES[current_theme]["bg"])
        while True:
            draw_window(title, logo.splitlines(), selected, menu)
            key = get_key()
            if key == "\x1b[A": selected = (selected - 1) % len(menu)
            elif key == "\x1b[B": selected = (selected + 1) % len(menu)
            elif key in ("\n", "\r"):
                choice = menu[selected].lower()
                if choice == "exit":
                    draw_window("EXITING...", ["Goodbye."])
                    time.sleep(0.2)
                    reset_terminal_bg()
                    clear()
                    reset_colors()
                    return
                elif choice == "appearance":
                    appearance_menu()
                elif choice == "settings":
                    settings_menu()
                elif choice == "start":
                    start_section()
                elif choice == "about":
                    about_screen()
    except KeyboardInterrupt:
        reset_terminal_bg()
        clear()
        reset_colors()
        print("Interrupted. Bye.")


if __name__ == "__main__":
    main()

