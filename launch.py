#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / "venv"
APP_DIR = ROOT / "App"
CLI_SCRIPT = ROOT / "CLI" / "CLI.py"
REQUIREMENTS = ROOT / "requirements.txt"

IS_WINDOWS = os.name == "nt"
VENV_PYTHON = VENV_DIR / ("Scripts/python.exe" if IS_WINDOWS else "bin/python3")


def color(text, code):
    if IS_WINDOWS:
        return text
    return f"\033[{code}m{text}\033[0m"


def banner():
    print(color("=" * 46, "36"))
    print(color("            IJAI PLATFORM LAUNCHER", "35"))
    print(color("=" * 46, "36"))


def has_venv():
    return VENV_PYTHON.exists()


def create_venv():
    print(color("Creating virtual environment...", "33"))
    subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)


def install_requirements():
    if not REQUIREMENTS.exists():
        return
    print(color("Installing Python dependencies (this may take a while)...", "33"))
    subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip"], check=False)
    subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(REQUIREMENTS)], check=False)


def ensure_env():
    if not has_venv():
        answer = input("No virtual environment found. Create one now? [Y/n] ").strip().lower()
        if answer in ("", "y", "yes"):
            create_venv()
            install_requirements()


def run_cli():
    if not CLI_SCRIPT.exists():
        print(color(f"CLI entrypoint not found: {CLI_SCRIPT}", "31"))
        return
    python_bin = str(VENV_PYTHON) if has_venv() else sys.executable
    subprocess.run([python_bin, str(CLI_SCRIPT)])


def npm_available():
    return shutil.which("npm") is not None


def run_app():
    if not npm_available():
        print(color("npm not found. Install Node.js first: https://nodejs.org", "31"))
        return

    node_modules = APP_DIR / "node_modules"
    if not node_modules.exists():
        print(color("Installing Electron app dependencies...", "33"))
        subprocess.run(["npm", "install"], cwd=str(APP_DIR), check=False)

    npm_cmd = "npm.cmd" if IS_WINDOWS else "npm"
    subprocess.run([npm_cmd, "start"], cwd=str(APP_DIR))


def run_installer():
    script = ROOT / "installer.sh"
    if IS_WINDOWS:
        print(color("Automated installer is only available on Linux/macOS.", "31"))
        return
    if not script.exists():
        print(color("installer.sh not found.", "31"))
        return
    subprocess.run(["bash", str(script)])


def menu():
    banner()
    print("1) Launch terminal CLI")
    print("2) Launch desktop app (Electron)")
    print("3) Run full installer (Linux/macOS)")
    print("4) Setup Python environment only")
    print("5) Exit")
    return input("\nChoose an option: ").strip()


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lstrip("-")
        if arg == "cli":
            ensure_env()
            run_cli()
            return
        if arg == "app":
            run_app()
            return
        if arg == "install":
            run_installer()
            return

    while True:
        choice = menu()
        if choice == "1":
            ensure_env()
            run_cli()
        elif choice == "2":
            run_app()
        elif choice == "3":
            run_installer()
        elif choice == "4":
            create_venv() if not has_venv() else print(color("Environment already exists.", "32"))
            install_requirements()
        elif choice == "5":
            break
        else:
            print(color("Invalid option.", "31"))
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye.")
