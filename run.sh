
# убиваем всё, что висит на 8000
fuser -k 8000/tcp 2>/dev/null

# запускаем сервер
python main.py