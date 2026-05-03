#!/bin/bash

# Список директорий для исключения (можно легко добавлять/удалять)
exclude_dirs=(
    "./.venv"
    # "./api"
    # "./app"
    "./config"
    # "./market"
    "./models"
    # "./processing"
    "./storage"
    "./utils"
    "./web"
)

# Функция для построения аргументов find с исключениями
build_find_excludes() {
    local args=()
    for dir in "${exclude_dirs[@]}"; do
        args+=(-path "$dir" -prune -o)
    done
    echo "${args[@]}"
}

# Основная команда
find . $(build_find_excludes) \
    -type f \
    \( -name "*.py" -o -name "*.yaml" -o -name "*.js" -o -name "*.css" -o -name "*.html" \) \
    -exec echo \; \
    -exec echo "=== {} ===" \; \
    -exec cat {} \; > code.txt

echo "Готово! Результат сохранён в code.txt"