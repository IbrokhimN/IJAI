#!/bin/bash
set -e

echo "=== Проверка и установка Ollama ==="

# Проверяем, есть ли ollama
if ! command -v ollama &> /dev/null; then
    echo "Ollama не найден. Скачиваем..."
    curl -LO https://ollama.com/downloads/ollama-linux
    chmod +x ollama-linux
    sudo mv ollama-linux /usr/local/bin/ollama
else
    echo "Ollama уже установлен"
fi

echo "=== Скачиваем модели ==="
MODELS=("llama3:latest" "codellama:latest")

for MODEL in "${MODELS[@]}"; do
    if ! ollama list | grep -q "$MODEL"; then
        echo "Скачиваем $MODEL ..."
        ollama pull "$MODEL"
    else
        echo "$MODEL уже загружена"
    fi
done

echo "=== Установка завершена ==="
ollama list
