#!/bin/bash
set -e

echo "=== Starting IJAI Installation ==="
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip ffmpeg espeak sox wget curl unzip libnss3 libatk1.0-0 libatk-bridge2.0-0 libxss1 libgtk-3-0

echo "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

echo "Installing Python dependencies from requirements.txt..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || true
deactivate

echo "Setting up global 'ijai' command..."
cat > ijai-cli << 'WRAPPER'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/venv/bin/activate"
python3 "$DIR/CLI/CLI.py" "$@"
WRAPPER
chmod +x ijai-cli
sudo ln -sf "$(pwd)/ijai-cli" /usr/local/bin/ijai

echo "=== IJAI Installation Complete! ==="
echo "Run IJAI: ijai"
echo "Or launch everything via: ./run.sh"
echo "To manually activate the Python virtual environment: source venv/bin/activate"
