echo "=== Starting IJAI Installation ==="
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip ffmpeg espeak sox wget curl unzip libnss3 libatk1.0-0 libatk-bridge2.0-0 libxss1 libgtk-3-0
echo "Creating Python virtual environment..."
python3 -m venv venv
echo "Activating virtual environment..."
source venv/bin/activate
echo "Installing Python dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo "Setting up global 'ijai' command..."
chmod +x ijai-cli
sudo ln -sf $(pwd)/ijai-cli /usr/local/bin/ijai
echo "=== IJAI Installation Complete! ==="
echo "Run IJAI: ijai"
echo "To manually activate the Python virtual environment: source venv/bin/activate"

