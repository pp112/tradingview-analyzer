# find frontend -type f -exec echo "=== {} ===" \; -exec cat {} \; > web_code.txt
find frontend/js -type f -exec echo "=== {} ===" \; -exec cat {} \; > web_code.txt
cat frontend/old_index.html >> web_code.txt
cat frontend/style.css >> web_code.txt