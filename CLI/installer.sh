#!/bin/bash
# IJAI Installer
# ======================
# Bash installer for IJAI project
# Sets up system dependencies, Python venv, Python packages,
# global CLI command, and downloads selected model.
set -e

# ANSI colors
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
CYAN="\033[36m"
BOLD="\033[1m"
RESET="\033[0m"

# ----------------------
# Print welcome message
# ----------------------
cat <<'EOF'
  /\_/\  
 ( o.o ) 
  > ^ <  
EOF

echo -e "${BOLD}${CYAN}=== IJAI Installer ===${RESET}\n"

# ----------------------
# Remove known problematic PPAs
# ----------------------
for ppa in neovim-ppa; do
    if grep -Rq "$ppa" /etc/apt/sources.list.d/; then
        echo "Removing $ppa..."
        sudo add-apt-repository --remove -y ppa:$ppa/stable || true
    fi
done

# ----------------------
# Update package lists
# ----------------------
sudo apt-get update -o Acquire::AllowInsecureRepositories=true -o Acquire::AllowDowngradeToInsecureRepositories=true || true

# ----------------------
# Install system dependencies
# ----------------------
sudo apt install -y git python3 python3-venv python3-pip ffmpeg espeak sox wget curl unzip \
libnss3 libatk1.0-0 libatk-bridge2.0-0 libxss1 libgtk-3-0 || true

# ----------------------
# Create Python virtual environment
# ----------------------
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# ----------------------
# Install Python packages
# ----------------------
source venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt || true
fi
deactivate

# ----------------------
# Setup global CLI command
# ----------------------
# We create a wrapper in the root that calls CLI/CLI.py with venv activated
cat > ijai-cli <<'EOF2'
#!/bin/bash
source "$(dirname "$0")/venv/bin/activate"
python3 "$(dirname "$0")/CLI/CLI.py" "$@"
EOF2

chmod +x ijai-cli
sudo ln -sf "$(pwd)/ijai-cli" /usr/local/bin/ijai

# ----------------------
# Download model with progress
# ----------------------
python3 <<'PYTHON_CODE'
import os, sys, requests
from shutil import get_terminal_size

# Create model folder
os.makedirs("llm", exist_ok=True)

# Check RAM
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

# Models
models = {
    "1": ("Phi-3-mini-4k-instruct-q4.gguf",
          "https://huggingface.co/IbrokhimNN/IJAI-models/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"),
    "2": ("Yi-1.5-6B-Chat-Q4_K_M.gguf",
          "https://huggingface.co/IbrokhimNN/IJAI-models/resolve/main/Yi-1.5-6B-Chat-Q4_K_M.gguf"),
    "3": ("gemma-7b.Q4_K_M.gguf",
          "https://huggingface.co/IbrokhimNN/IJAI-models/resolve/main/gemma-7b.Q4_K_M.gguf")
}

# List models
print("\nAvailable models:")
for k,v in models.items():
    print(f"{k}. {v[0]}")

choice = input("Enter model number: ").strip()
if choice not in models:
    print("Invalid choice")
    sys.exit(1)

name, url = models[choice]
filepath = os.path.join("llm", name)

# Download function with progress bar
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

# ----------------------
# Finish
# ----------------------
echo -e "\nIJAI installation complete"
echo "Run IJAI: ijai"
echo "Activate venv manually: source venv/bin/activate"

