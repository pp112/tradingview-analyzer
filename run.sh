kill -9 $(lsof -ti :8000) 2>/dev/null

python main.py