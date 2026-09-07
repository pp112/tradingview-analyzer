# find frontend/src -type f -exec echo "=== {} ===" \; -exec cat {} \; > web_code.txt

find frontend/src/features/positions-orders -type f ! -name *stories.tsx -exec echo "=== {} ===" \; -exec cat {} \; > web_code.txt
