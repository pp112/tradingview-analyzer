# 📁 1. Структура проекта

```
crypto_analytics/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── __init__.py
│   ├── websocket_client.py
│   ├── data_fetcher.py
│   └── data_storage.py
│
├── indicators/
│   ├── __init__.py
│   ├── sma.py
│   ├── ema.py
│   └── correlation.py
│
├── analysis/
│   ├── __init__.py
│   ├── crossover_detector.py
│   └── analyzer.py
│
├── visualization/
│   ├── __init__.py
│   ├── plotter.py
│   └── table_renderer.py
│
└── utils/
    ├── __init__.py
    ├── logger.py
    └── helpers.py
```

---

# 🧠 2. Описание модулей и классов

Разберем по слоям (как в реальном проекте)

---

# 🚀 main.py

### Класс: `App`

**Что делает:**

* Точка входа
* Оркестрирует весь процесс

```python
class App:
    def run(self):
        # 1. Получить данные
        # 2. Посчитать индикаторы
        # 3. Найти пересечения
        # 4. Построить графики
        # 5. Вывести таблицу
        pass
```

---

# ⚙️ config.py

### Класс: `Config`

```python
class Config:
    SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    INTERVAL = "1h"
    EMA_PERIOD = 20
    SMA_PERIOD = 50
```

---

# 📡 data/

## websocket_client.py

### Класс: `TradingViewWebSocketClient`

**Что делает:**

* Подключается к TradingView через WebSocket
* Получает исторические данные

```python
class TradingViewWebSocketClient:
    def connect(self): pass
    def subscribe(self, symbol): pass
    def get_historical_data(self, symbol): pass
```

---

## data_fetcher.py

### Класс: `DataFetcher`

**Что делает:**

* Управляет получением данных
* Абстрагирует источник данных

```python
class DataFetcher:
    def __init__(self, client):
        self.client = client

    def fetch_all(self, symbols):
        # возвращает dict с данными по всем криптовалютам
        pass
```

---

## data_storage.py

### Класс: `DataStorage`

**Что делает:**

* Хранит данные в памяти или файлах

```python
class DataStorage:
    def save(self, symbol, data): pass
    def load(self, symbol): pass
```

---

# 📊 indicators/

## sma.py

### Класс: `SMAIndicator`

```python
class SMAIndicator:
    def calculate(self, prices, period):
        pass
```

---

## ema.py

### Класс: `EMAIndicator`

```python
class EMAIndicator:
    def calculate(self, prices, period):
        pass
```

---

## correlation.py

### Класс: `CorrelationCalculator`

```python
class CorrelationCalculator:
    def calculate(self, base_asset, other_assets):
        # считает корреляцию с BTC
        pass
```

---

# 🧪 analysis/

## crossover_detector.py

### Класс: `CrossoverDetector`

**Что делает:**

* Определяет пересечения EMA и SMA

```python
class CrossoverDetector:
    def find_crossovers(self, ema, sma):
        # возвращает список сигналов
        pass
```

---

## analyzer.py

### Класс: `MarketAnalyzer`

**Что делает:**

* Центральная логика анализа

```python
class MarketAnalyzer:
    def __init__(self, sma, ema, corr, crossover):
        self.sma = sma
        self.ema = ema
        self.corr = corr
        self.crossover = crossover

    def analyze(self, market_data):
        # 1. считаем SMA/EMA
        # 2. считаем корреляцию
        # 3. ищем пересечения
        pass
```

---

# 📈 visualization/

## plotter.py

### Класс: `Plotter`

**Что делает:**

* Строит графики (например через matplotlib или plotly)

```python
class Plotter:
    def plot_price_with_indicators(self, prices, sma, ema):
        pass
```

---

## table_renderer.py

### Класс: `TableRenderer`

**Что делает:**

* Выводит таблицу корреляций

```python
class TableRenderer:
    def render_correlation_table(self, correlations):
        pass
```

---

# 🛠 utils/

## logger.py

### Класс: `Logger`

```python
class Logger:
    def info(self, msg): pass
    def error(self, msg): pass
```

---

## helpers.py

### Класс: `DataUtils`

```python
class DataUtils:
    @staticmethod
    def normalize(data): pass
```

---

# 🔄 Как всё работает вместе

Простой pipeline:

```
WebSocket → DataFetcher → Analyzer → Visualization
```

---

# 🧩 Пример сценария выполнения

```python
app = App()
app.run()
```

Внутри:

1. Получили данные BTC, ETH, BNB
2. Посчитали:

   * EMA
   * SMA
   * корреляции с BTC
3. Нашли пересечения EMA/SMA
4. Построили график
5. Вывели таблицу

---

# 💡 Почему такая архитектура хороша

* 🔹 легко добавить новые индикаторы (RSI, MACD)
* 🔹 можно заменить TradingView на Binance API
* 🔹 удобно тестировать каждый модуль отдельно
* 🔹 чистое разделение ответственности

---

# 🚀 Если хочешь дальше

Могу следующим шагом:

* написать **реализацию EMA/SMA**
* или показать **пример WebSocket подключения к TradingView**
* или собрать **минимально рабочий MVP (код целиком)**
