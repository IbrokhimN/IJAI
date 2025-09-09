#!/bin/bash
set -e

echo "=== Проверка и установка Ollama ==="

if ! command -v ollama &> /dev/null; then
    echo "Ollama не найден. Устанавливаем..."
    curl -fsSL https://ollama.com/download/OllamaLinuxInstaller.sh | sh
else
    echo "Ollama уже установлен"
fi

echo "=== Скачиваем модели ==="
MODELS=("llama3" "codellama")

for MODEL in "${MODELS[@]}"; do
    if ! ollama list | awk '{print $1}' | grep -q "^$MODEL$"; then
        echo "Скачиваем $MODEL ..."
        ollama pull "$MODEL"
    else
        echo "$MODEL уже загружена"
    fi
done

echo "=== Установка завершена ==="
ollama list
