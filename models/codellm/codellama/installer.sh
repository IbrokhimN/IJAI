#!/bin/bash
set -e

echo "=== Проверка и установка Ollama ==="
if ! command -v ollama &> /dev/null; then
    echo "Ollama не найден. Скачиваем..."
    curl -LO https://ollama.com/downloads/ollama-linux
    chmod +x ollama-linux
    sudo mv ollama-linux /usr/local/bin/ollama
else
    echo "Ollama уже установлен"
fi

echo "=== Скачиваем модель codellama:latest ==="

MODEL="codellama:latest"
if ! ollama list | grep -q "$MODEL"; then
    echo "Скачиваем $MODEL ..."
    ollama pull "$MODEL"
else
    echo "$MODEL уже загружена"
fi

echo "=== Установка завершена ==="
ollama list
