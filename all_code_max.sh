find . \( -path "./.venv" -o -path "./web" -prune \) -prune -o \( -name "*.py" -o -name "*.yaml" \) -type f -exec echo \; -exec echo "=== {} ===" \; -exec cat {} \; > code.txt

# find . -path "./.venv" -prune -o \( -name "*.py" -o -name "*.yaml" \) -type f -exec echo \; -exec echo "=== {} ===" \; -exec cat {} \; > code.txt