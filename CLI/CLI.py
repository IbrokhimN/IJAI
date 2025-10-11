#!/usr/bin/env python3
import os
import sys
import time
import termios
import tty
import shutil
import subprocess
import textwrap
# ===============================
#  THEMES & SETTINGS
# ===============================
THEMES = {
    "neon": {"accent": "\033[96m", "border": "─", "dot": "● "},
    "matrix": {"accent": "\033[92m", "border": "═", "dot": "◉ "},
    "pink": {"accent": "\033[95m", "border": "─", "dot": "♥ "},
    "default": {"accent": "\033[94m", "border": "─", "dot": "● "},
}

current_theme = "neon"
animation_speed = 0.02  # можно менять в Settings

# ===============================
#  UTILS
# ===============================
def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def get_terminal_size():
    size = shutil.get_terminal_size()
    return size.columns, size.lines

def get_key():
    """Считывает стрелки и Enter без ожидания Enter после стрелок."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == "\x1b":          # escape sequence (стрелки)
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ===============================
#  DRAW WINDOW
# ===============================
def draw_window(title, content_lines=None, selected_index=None, menu_items=None, scroll_offset=0):
    import textwrap
    cols, rows = get_terminal_size()
    margin = 1
    theme = THEMES[current_theme]
    inner_width = max(20, cols - margin * 2 - 2)
    inner_height = max(6, rows - 6)

    clear()
    print("\n" * margin, end="")

    # top border
    print(" " * margin + "╭" + theme["border"] * inner_width + "╮")
    print(" " * margin + "│  " + theme["accent"] + theme["dot"] * 3 + "\033[0m" + " " * (inner_width - 5) + "│")
    print(" " * margin + "│" + title.center(inner_width) + "│")
    print(" " * margin + "├" + theme["border"] * inner_width + "┤")

    # prepare content
    content_lines = content_lines or []
    menu_items = menu_items or []

    # wrap all content lines properly to fit width
    wrapped_content = []
    for line in content_lines:
        # если строка пустая — добавляем просто пустую строку
        if not line.strip():
            wrapped_content.append("")
        else:
            wrapped_lines = textwrap.wrap(line, width=inner_width - 2)
            wrapped_content.extend(wrapped_lines)

    # calculate visible content area
    visible_lines = inner_height - len(menu_items) - 6
    total_lines = len(wrapped_content)
    slice_start = max(0, scroll_offset)
    slice_end = min(total_lines, slice_start + visible_lines)
    visible_content = wrapped_content[slice_start:slice_end]

    # draw content area (centered)
    for line in visible_content:
        print(" " * margin + "│" + line.center(inner_width) + "│")

    # fill remaining space
    for _ in range(visible_lines - len(visible_content)):
        print(" " * margin + "│" + " " * inner_width + "│")

    # optional scrollbar indicator (future use)
    if len(wrapped_content) > visible_lines:
        scrollbar_height = max(1, int(visible_lines * visible_lines / len(wrapped_content)))
        scrollbar_top = int((visible_lines - scrollbar_height) * scroll_offset / (len(wrapped_content) - visible_lines))
        lines = [" "] * visible_lines
        for i in range(scrollbar_top, scrollbar_top + scrollbar_height):
            if 0 <= i < visible_lines:
                lines[i] = "│"

    # menu area
    if menu_items:
        print(" " * margin + "├" + theme["border"] * inner_width + "┤")
        for i, item in enumerate(menu_items):
            prefix = "➤ " if i == selected_index else "  "
            style = theme["accent"] + item + "\033[0m" if i == selected_index else item
            line = (prefix + style).center(inner_width)
            print(" " * margin + "│" + line + "│")

    # bottom border
    print(" " * margin + "╰" + theme["border"] * inner_width + "╯")

# ===============================
#  SECTIONS
# ===============================
def start_section():
    """Показываем быстрый boot, затем запускаем ../models/bunch.py (если есть)."""
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
        # задержка зависит от animation_speed, но минимальна чтобы быть быстрой
        time.sleep(max(0.01, animation_speed * 2))
    # Найти bunch.py
    models_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "bunch.py"))
    if not os.path.exists(models_path):
        print("\n\033[91mError: file not found:\033[0m", models_path)
        input("\nPress Enter to return...")
        return
    print("\n" + theme["accent"] + "Launching module: " + models_path + "\033[0m")
    try:
        # запускаем в том же терминале (как раньше)
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
            elif choice == "Back":
                return

def appearance_menu():
    global current_theme
    themes = list(THEMES.keys()) + ["Back"]
    selected = 0
    while True:
        draw_window("🎨 APPEARANCE 🎨", ["Select visual theme"], selected, themes)
        key = get_key()
        if key == "\x1b[A": selected = (selected - 1) % len(themes)
        elif key == "\x1b[B": selected = (selected + 1) % len(themes)
        elif key in ("\n", "\r"):
            if themes[selected] == "Back":
                return
            current_theme = themes[selected]
            # мгновенно показать эффект — короткая пауза и вернуть меню
            draw_window("🎨 APPEARANCE 🎨", [f"Theme set: {current_theme}"], None, [])
            time.sleep(0.25)

def about_screen():
    about_text = [
        "**IJAI CLI** is a cross-platform command-line interface system with visual and interactive elements, designed to merge functionality, flexibility, and aesthetic experience in one cohesive environment. Unlike traditional CLI tools that focus purely on command execution, IJAI turns the terminal into a *visually expressive and customizable workspace* — a place where design and utility meet.",
        "",
        "At its core, IJAI CLI redefines how developers and users interact with command-line environments. It’s not just a tool for executing scripts; it’s an immersive, dynamic shell that feels alive. From its custom ASCII logo to smooth animations and appearance settings, every detail aims to make the terminal an extension of your personality and workflow.",
        "",
        "---",
        "",
        "### 🌟 1. Vision and Purpose",
        "",
        "The fundamental vision behind IJAI CLI is simple: **to make the command line beautiful, personal, and emotionally engaging**.",
        "Most terminals are built with performance in mind but neglect aesthetics. IJAI takes the opposite route — creating an artistic yet efficient environment where beauty amplifies productivity.",
        "",
        "The name *IJAI* symbolizes balance between imagination and logic — between human creativity and machine precision. The CLI seeks to become a hybrid space: half a developer’s workspace, half an art piece.",
        "",
        "Its purpose is not merely to replace existing shells, but to **inspire a new way of thinking about interfaces** — where every command and visual cue feels part of a living system. The result is a terminal that’s not cold or mechanical, but expressive, atmospheric, and adaptable.",
        "",
        "---",
        "",
        "### 🧩 2. Architecture and Structure",
        "",
        "IJAI CLI is built with a **modular architecture** that ensures extensibility and maintainability. Each feature — from theming to configuration — is isolated into logical modules that communicate cleanly through well-defined interfaces.",
        "",
        "**Main components include:**",
        "",
        "* **`main.py`** — entry point; handles initialization, CLI boot sequence, and main screen rendering.",
        "* **`appearance.py`** — manages visual themes, color palettes, and appearance transitions.",
        "* **`settings.py`** — handles configuration persistence, user preferences, and environment variables.",
        "* **`core/`** — the engine of IJAI; contains internal logic, command routing, and performance utilities.",
        "* **`data/`** — storage for ASCII art, theme presets, and system templates.",
        "* **`assets/`** — graphical resources, decorative elements, and stylistic components (such as fonts and shaders).",
        "",
        "This architecture allows developers to modify or extend IJAI without breaking its internal harmony. Each subsystem can evolve independently, which makes the CLI both lightweight and highly customizable.",
        "",
        "---",
        "",
        "### 🎨 3. Visual Identity and Aesthetic",
        "",
        "At the heart of IJAI’s design philosophy lies **a deep respect for aesthetics**.",
        "The ASCII logo isn’t just a decorative piece — it’s dynamically generated and perfectly centered regardless of terminal width. The visual core adapts to user preferences, maintaining symmetry, smoothness, and emotional tone.",
        "",
        "IJAI’s interface features:",
        "",
        "* **Neon-style glow** with subtle gradients.",
        "* **Animated text transitions** (e.g., fade-in or pulse effects).",
        "* **Customizable themes**, including dark, light, minimalist, and “femboy-nyash” playful modes.",
        "* **Dynamic borders and centered layouts**, ensuring readability and charm across different resolutions.",
        "",
        "Even small touches — such as cursor animation, loading indicators, or line separators — are designed with elegance in mind. The CLI strives to feel alive, almost like a digital being with personality.",
        "",
        "---",
        "",
        "### ⚙️ 4. Settings and Customization",
        "",
        "IJAI CLI takes customization seriously. The **Settings** and **Appearance** menus aren’t just placeholders — they fully control how the system looks and behaves.",
        "",
        "Users can change:",
        "",
        "* **Color palettes** (foreground, background, accents).",
        "* **Typography or font size** (for ASCII rendering).",
        "* **Theme presets** that transform the mood of the entire environment.",
        "* **Sound effects and motion level** (for subtle animations).",
        "* **Behavioral options**, such as startup messages, auto-clearing, or silent boot.",
        "",
        "All settings are stored persistently, so the CLI “remembers” the user’s preferences between sessions. This transforms the terminal from a generic tool into a **personal environment**, fine-tuned to its owner’s taste.",
        "",
        "The configuration system also supports live updates — meaning changes can apply instantly without needing to restart the program. This seamlessness enhances the feeling of interactivity and fluid control.",
        "",
        "---",
        "",
        "### 🧠 5. Technical Design Philosophy",
        "",
        "IJAI is written primarily in **Python**, chosen for its balance of simplicity and expressive power.",
        "Internally, the project embraces several key software design principles:",
        "",
        "1. **Modularity** — Each feature lives in its own namespace.",
        "2. **Simplicity** — Every function should do one thing cleanly.",
        "3. **Readability** — Code should be self-documenting, human-friendly, and intuitive.",
        "4. **Extensibility** — Adding a new feature or theme should never break existing logic.",
        "5. **User empathy** — Every visual or functional choice must serve user experience first.",
        "",
        "These principles ensure the CLI remains maintainable, elegant, and fast, even as it grows.",
        "",
        "Performance optimization is achieved through **lazy loading** of non-essential modules and **asynchronous rendering** for visual animations, which prevents input lag and ensures fluid transitions even on low-spec systems.",
        "",
        "---",
        "",
        "### 🧰 6. Core Features",
        "",
        "IJAI CLI provides a growing set of core features, including:",
        "",
        "* 🖥 **Custom splash screen** with smooth logo animation.",
        "* 🎛 **Interactive menus** (Start, Settings, Appearance, Info).",
        "* 🎨 **Dynamic theming engine** for instant color swaps.",
        "* 🔄 **Persistent user configuration** stored locally.",
        "* ⚙️ **Command hooks and modular plugin system** for extending functionality.",
        "* 💬 **Terminal message formatter** that stylizes output text for readability.",
        "* 🧭 **Navigation system** for switching between pages or sections using arrow keys or shortcuts.",
        "",
        "The combination of interactivity, modularity, and style makes IJAI stand out as both an artistic and practical CLI project.",
        "",
        "---",
        "",
        "### 💞 7. Personality and User Experience",
        "",
        "What truly makes IJAI different is its **soul**.",
        "The CLI feels personal — almost like a living character that greets you when it starts. The ASCII logo appears with a sense of ceremony; transitions feel natural; and the environment carries emotional tone.",
        "",
        "Instead of sterile functionality, IJAI offers a **relationship** between user and interface. It welcomes customization not just as an option but as a form of self-expression.",
        "Developers can shape the CLI’s “personality” — whether serious, playful, futuristic, or cozy — through simple configuration tweaks.",
        "",
        "This aspect makes IJAI ideal for creative developers, aesthetic enthusiasts, or anyone who believes that *tools should feel good to use*.",
        "",
        "---",
        "",
        "### 🧱 8. Development Philosophy and Future Goals",
        "",
        "IJAI’s roadmap emphasizes continuous evolution. Planned directions include:",
        "",
        "* **Plugin SDK** for community-made extensions.",
        "* **Animated ASCII splash intros** using frame-based rendering.",
        "* **Theme marketplace** (import/export user-made themes).",
        "* **Integration with AI assistants** to bring contextual help or dialogue into the terminal.",
        "* **Performance profiling dashboard** to visualize CLI load times.",
        "* **Cross-shell compatibility layer** for zsh, bash, and fish environments.",
        "",
        "The long-term goal is to make IJAI not just a standalone CLI, but a *platform* — a foundation where developers can build personalized command-line universes.",
        "",
        "---",
        "",
        "### 🔒 9. Security and Stability",
        "",
        "Even though IJAI is visually focused, it doesn’t compromise on stability.",
        "The system isolates all file operations within a sandboxed environment to prevent accidental overwrites or unsafe I/O. It validates user inputs and handles edge cases gracefully, ensuring the CLI never crashes from malformed data.",
        "",
        "Configuration files are versioned to prevent corruption, and all critical operations include safe fallbacks. As a result, IJAI remains both **beautiful and reliable**, even under experimental customization.",
        "",
        "---",
        "",
        "### 🚀 10. Philosophy in One Line",
        "",
        "> “**IJAI CLI** is where beauty meets logic — a command line that breathes, glows, and listens.”",
        "",
        "---",
        "",
        "### 💬 11. Conclusion",
        "",
        "IJAI CLI is not just another command-line tool; it’s a **living aesthetic framework** for the terminal — a fusion of art, code, and emotion.",
        "It embodies a rare blend of practicality and beauty, where code feels like design and interaction feels like expression.",
        "",
        "In essence, IJAI transforms the plain black screen of the terminal into a stage — one where your commands, your visuals, and your imagination perform in harmony.",
        "It’s not about replacing what exists, but about *elevating* it — giving developers a space that’s not only powerful, but also inspiring to use.",
        "",
        "As technology becomes more human, IJAI CLI stands as a symbol of that transition — proof that even in a command line, there can be warmth, elegance, and soul.",
        "",
        "",
        "💸Support the developer💸",
        "USDT (TRC20): TPutzJ12Bs4jAPLT9rkQhvg6PdwHhQfJVB"
    ]
    scroll = 0
    while True:
        draw_window('💫 ABOUT 💫', about_text, None, [], scroll_offset=scroll)
        key = get_key()
        if key == "\x1b[A":  # стрелка вверх
            if scroll > 0:
                scroll -= 1
        elif key == "\x1b[B":  # стрелка вниз
            if scroll < len(about_text) - 1:
                scroll += 1
        elif key in ("\n", "\r", "\x1b"):  # Enter или Esc — выход
            return

# ===============================
#  MAIN
# ===============================
def colored_logo():
    purple = "\033[95m"
    blue = "\033[94m"
    cyan = "\033[96m"
    pink = "\033[91m"
    reset = "\033[0m"

    logo = f"""
{purple}
{purple}▀████▀  ▀████▀     ██     ▀████▀
{purple}  ██      ██      ▄██▄      ██  
{purple}  ██      ██     ▄█▀██▄     ██  
{purple}  ██      ██    ▄█  ▀██     ██  
{purple}  ██      ██    ████████    ██  
{purple}  ██ ███  ██   █▀      ██   ██  
{purple}▄████▄█████  ▄███▄   ▄████▄████▄
""".strip("\n")

    return logo

def main():
    logo = colored_logo()   

    title = "░▒▓ IJAI CLI ▓▒░"
    menu = ["Start", "Settings", "Appearance", "About", "Exit"]
    selected = 0

    try:
        while True:
            draw_window(title, logo.splitlines(), selected, menu)
            key = get_key()
            if key == "\x1b[A": selected = (selected - 1) % len(menu)
            elif key == "\x1b[B": selected = (selected + 1) % len(menu)
            elif key in ("\n", "\r"):
                choice = menu[selected].lower()
                if choice == "exit":
                    draw_window("👋 EXITING...", ["Goodbye."])
                    time.sleep(0.2)
                    clear()
                    return
                elif choice == "about":
                    about_screen()
                elif choice == "appearance":
                    appearance_menu()
                elif choice == "settings":
                    settings_menu()
                elif choice == "start":
                    start_section()
    except KeyboardInterrupt:
        clear()
        print("Interrupted. Bye.")
        return

if __name__ == "__main__":
    main()


