#!/bin/bash

# Список директорий, которые НУЖНО обрабатывать
include_dirs=(
    "./backend/api"
    "./backend/app"
    "./backend/config"
    "./backend/exchanges"
    "./backend/market"
    "./backend/models"
    "./backend/positions"
    "./backend/processing"
    "./backend/storage"
    "./backend/utils"
)

# Основная команда
find "${include_dirs[@]}" \
    -type f \
    \( -name "*.py" -o -name "*.yaml" -o -name "*.js" -o -name "*.css" -o -name "*.html" \) \
    -exec echo \; \
    -exec echo "=== {} ===" \; \
    -exec cat {} \; > code.txt

echo "Готово! Результат сохранён в code.txt"