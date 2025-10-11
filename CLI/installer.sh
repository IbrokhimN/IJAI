# installer for cli ( i'll add coments soon )
set -e
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI_FILE="$BASE_DIR/CLI.py"
if ! command -v python3 &> /dev/null; then
    echo "Python3 не найден! Установите Python 3 и повторите."
    exit 1
fi
BIN_DIR="$BASE_DIR/bin"
mkdir -p "$BIN_DIR"

CLI_WRAPPER="$BIN_DIR/ijai_cli"

# im sorry for what im gonna do rn
cat > "$CLI_WRAPPER" <<EOL
#!/bin/bash
# Активируем venv на один уровень выше
source "$BASE_DIR/../venv/bin/activate"
python3 "$CLI_FILE" "\$@"
EOL

chmod +x "$CLI_WRAPPER"

if ! grep -q "$BIN_DIR" ~/.bashrc; then
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> ~/.bashrc
fi
if ! grep -q "$BIN_DIR" ~/.zshrc; then
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> ~/.zshrc
fi

echo "Done!"

