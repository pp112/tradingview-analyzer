#!/bin/bash

# Список директорий, которые НУЖНО обрабатывать
include_dirs=(
    # "./api"
    # "./app"
    # "./config"
    # "./market"
    # "./models"
    # "./processing"
    # "./storage"
    # "./utils"
    "./web"
)

# Основная команда
find "${include_dirs[@]}" \
    -type f \
    \( -name "*.py" -o -name "*.yaml" -o -name "*.js" -o -name "*.css" -o -name "*.html" \) \
    -exec echo \; \
    -exec echo "=== {} ===" \; \
    -exec cat {} \; > code.txt

echo "Готово! Результат сохранён в code.txt"