#!/bin/bash

# Список директорий, которые НУЖНО обрабатывать
include_dirs=(
    "./backend/api"
    "./backend/app"
    "./backend/config"
    "./backend/exchanges"
    "./backend/market"
    "./backend/models"
    "./backend/processing"
    "./backend/schemas"
    "./backend/signal_links"
    "./backend/storage"
    "./backend/utils"
    "./frontend/src"
)

find "${include_dirs[@]}" \
    -type f \
    \( -name "*.py" -o -name "*.yaml" -o -name "*.tsx" -o -name "*.ts" -o -name "*.css" -o -name "*.html" \) \
    -exec echo \; \
    -exec echo "=== {} ===" \; \
    -exec cat {} \; > code.txt

echo "Готово! Результат сохранён в code.txt"