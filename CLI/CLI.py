import os
import shutil
import subprocess
import sys

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def center(text):
    cols = shutil.get_terminal_size().columns
    return "\n".join(line.center(cols) for line in text.splitlines())

def main():
    clear()
    
    logo = r"""
                                
▀████▀  ▀████▀     ██     ▀████▀
  ██      ██      ▄██▄      ██  
  ██      ██     ▄█▀██▄     ██  
  ██      ██    ▄█  ▀██     ██  
  ██      ██    ████████    ██  
  ██ ███  ██   █▀      ██   ██  
▄████▄█████  ▄███▄   ▄████▄████▄
                                
                                

""".strip("\n")

    # рамка вокруг логотипа
    cols = shutil.get_terminal_size().columns
    print("╔" + "═"*(cols-2) + "╗")
    for line in logo.splitlines():
        print("║" + line.center(cols-2) + "║")
    print("╚" + "═"*(cols-2) + "╝")

    print()
    print(center(" ░▒▓ CLI ▓▒░ "))
    print("\n" + "─" * cols)
    print(center("[ НАЧАТЬ ]"))
    input(center("Нажмите Enter, чтобы запустить... "))

    clear()
    print("╔══[ Инициализация нейросетевого ядра ]══════════════════════════╗")
    print("║ ░▒▓ Loading models from models/ ▓▒░ ..................... [OK] ║")
    print("║ ░▒▓ Loading bunch.py ▓▒░ ................................ [OK] ║")
    print("║ ░▒▓ Synchronizing internal structures ▓▒░ ............. [DONE] ║")
    print("║ ░▒▓ Starting IJAI system ▓▒░ ......................... [READY] ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    models_path = os.path.join(os.path.dirname(__file__), "..", "models", "bunch.py")
    models_path = os.path.abspath(models_path)

    if not os.path.exists(models_path):
        print(f"файл не найден: {models_path}")
        sys.exit(1)

    subprocess.run([sys.executable, models_path])

if __name__ == "__main__":
    main()


