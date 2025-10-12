#!/bin/bash
# IJAI Installer
# ======================
# Bash installer for IJAI project
# Works on Debian/Ubuntu, Fedora, Arch, SUSE
# Sets up system dependencies, Python venv, Python packages,
# global CLI command, and downloads selected model.

set -e  # die if anything fails. don't be lazy

# colors, because why not
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
CYAN="\033[36m"
BOLD="\033[1m"
RESET="\033[0m"

# print welcome
cat <<'EOF'
  /\_/\  
 ( o.o ) 
  > ^ <  
EOF

echo -e "${BOLD}${CYAN}=== IJAI Installer ===${RESET}\n"

# detect OS, minimal brain required
OS_TYPE=""
if [ -f /etc/os-release ]; then
    . /etc/os-release
    case "$ID" in
        ubuntu|debian) OS_TYPE="debian";;
        fedora) OS_TYPE="fedora";;
        arch) OS_TYPE="arch";;
        opensuse*|suse) OS_TYPE="suse";;
        *) echo -e "${RED}Unsupported OS: $ID${RESET}"; exit 1;;
    esac
else
    echo -e "${RED}Cannot detect OS${RESET}"; exit 1
fi
echo -e "${CYAN}Detected OS: $OS_TYPE${RESET}"

# detect architecture. it's either x86_64 or ARM, simple
ARCH=$(uname -m)
echo -e "${CYAN}Detected architecture: $ARCH${RESET}"

# install dependencies. pick your distro and stop whining
echo -e "${CYAN}Installing system dependencies...${RESET}"
case "$OS_TYPE" in
    debian)
        sudo apt update -o Acquire::AllowInsecureRepositories=true -o Acquire::AllowDowngradeToInsecureRepositories=true || true
        sudo apt install -y git python3 python3-venv python3-pip ffmpeg espeak sox wget curl unzip \
        libnss3 libatk1.0-0 libatk-bridge2.0-0 libxss1 libgtk-3-0 || true
        ;;
    fedora)
        sudo dnf install -y git python3 python3-virtualenv python3-pip ffmpeg espeak sox wget curl unzip \
        nss atk atk-bridge xorg-x11-server-Xvfb gtk3 || true
        ;;
    arch)
        sudo pacman -Syu --noconfirm git python python-virtualenv python-pip ffmpeg espeak sox wget curl unzip \
        nss atk gtk3 xorg-x11-server-Xvfb || true
        ;;
    suse)
        sudo zypper refresh
        sudo zypper install -y git python3 python3-virtualenv python3-pip ffmpeg espeak sox wget curl unzip \
        mozilla-nss atk atk-bridge gtk3 || true
        ;;
esac

# create virtual env if it doesn't exist. duh
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# install Python packages, don't break this
source venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt || true
fi
deactivate

# global CLI wrapper. simple, don't complain
cat > ijai-cli <<'EOF2'
#!/bin/bash
source "$(dirname "$0")/venv/bin/activate"
python3 "$(dirname "$0")/CLI/CLI.py" "$@"
EOF2

chmod +x ijai-cli
sudo ln -sf "$(pwd)/ijai-cli" /usr/local/bin/ijai

# download model. pick based on architecture and RAM
python3 <<PYTHON_CODE
import os, sys, requests
from shutil import get_terminal_size
import platform

os.makedirs("llm", exist_ok=True)

# check RAM, don't try to run 7b model on a potato
try:
    with open("/proc/meminfo") as f:
        ram_total = int(f.readline().split()[1]) // 1024
except:
    ram_total = 0

print(f"Available RAM: {ram_total // 1024} GB")
if ram_total < 8000:
    print("Recommended: light model")
elif ram_total < 16000:
    print("Medium model should work")
else:
    print("Any model can run")

arch = platform.machine()
print(f"Detected architecture: {arch}")

# model mapping, stupid simple
models = {
    "x86_64": {
        "1": ("Phi-3-mini-4k-instruct-q4.gguf",
              "https://huggingface.co/IbrokhimNN/IJAI-models/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"),
        "2": ("Yi-1.5-6B-Chat-Q4_K_M.gguf",
              "https://huggingface.co/IbrokhimNN/IJAI-models/resolve/main/Yi-1.5-6B-Chat-Q4_K_M.gguf"),
        "3": ("gemma-7b.Q4_K_M.gguf",
              "https://huggingface.co/IbrokhimNN/IJAI-models/resolve/main/gemma-7b.Q4_K_M.gguf")
    },
    "aarch64": {
        "1": ("Phi-3-mini-4k-instruct-q4-aarch64.gguf",
              "https://huggingface.co/IbrokhimNN/IJAI-models/resolve/main/Phi-3-mini-4k-instruct-q4-aarch64.gguf"),
        "2": ("Yi-1.5-6B-Chat-Q4_K_M-aarch64.gguf",
              "https://huggingface.co/IbrokhimNN/IJAI-models/resolve/main/Yi-1.5-6B-Chat-Q4_K_M-aarch64.gguf"),
        "3": ("gemma-7b.Q4_K_M-aarch64.gguf",
              "https://huggingface.co/IbrokhimNN/IJAI-models/resolve/main/gemma-7b.Q4_K_M-aarch64.gguf")
    }
}

if arch not in models:
    print("Architecture not recognized, defaulting to x86_64 models")
    arch = "x86_64"

print("\nAvailable models:")
for k,v in models[arch].items():
    print(f"{k}. {v[0]}")

choice = input("Enter model number: ").strip()
if choice not in models[arch]:
    print("Invalid choice")
    sys.exit(1)

name, url = models[arch][choice]
filepath = os.path.join("llm", name)

# stupid progress bar
def download(url, path):
    r = requests.get(url, stream=True)
    total = int(r.headers.get("content-length", 0))
    downloaded = 0
    width = get_terminal_size((80,20)).columns - 10
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                done = int(width*downloaded/total) if total else 0
                bar = f"[{'='*done}{' '*(width-done)}]"
                print(f"\r{bar} {downloaded//1024//1024}MB / {total//1024//1024}MB", end="")
    print("\nModel saved!")

download(url, filepath)
PYTHON_CODE

# done
echo -e "\nIJAI installation complete"
echo "Run IJAI: ijai"
echo "Activate venv manually: source venv/bin/activate"
