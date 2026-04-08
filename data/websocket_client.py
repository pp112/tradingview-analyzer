import random
import string
import json
import re
import time
import logging
from enum import Enum
from typing import TypedDict
from websocket import create_connection

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(message)s"
)


class Timeframe(Enum):
    M30 = "30"
    H1 = "60"
    H4 = "240"
    D1 = "1D"


class TOHLC(TypedDict):
    timestamp: int
    open: float
    high: float
    low: float
    close: float


class TradingViewWebSocket:
    """
    Класс для подключения к WebSocket TradingView и получения исторических данных.
    """
    def __init__(self):
        self._ws = None
        self._chart_session = None
        self._quote_session = None
        self._i_total = 1
        self._i = 1

    def __enter__(self):
        self._connect()
        self._setup_sessions()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._ws.close()
        return False

    def get_historical_bars(
        self,
        symbol: str = "BTCUSDT.P",
        timeframe: Timeframe = Timeframe.H1
    ) -> list[TOHLC] | None:
        """
        Получает исторические данные (TOHLC) для указанного символа и таймфрейма.
        """
        if self._i > 100:
            self._reconnect()

        self._request_historical_data(symbol, timeframe)

        msg = self._wait_for_historical_data(symbol)
        self._i += 1
        self._i_total += 1
        if not msg:
            return None
        
        return self._extract_price_bars(msg)

    def _connect(self):
        headers = {
            'Connection': 'Upgrade',
            'Host': 'data.tradingview.com',
            'Origin': 'https://data.tradingview.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56',
            'Upgrade': 'websocket'
        }

        self._ws = create_connection("wss://data.tradingview.com/socket.io/websocket", headers=headers)

    def _reconnect(self):
        logger.info("Переподключение к TradingView WebSocket...")
        try:
            if self._ws:
                self._ws.close()
        except Exception:
            pass

        self._connect()
        self._setup_sessions()
        self._i = 1

    @staticmethod
    def _generate_string_session(prefix):
        random_string = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))
        return prefix + random_string
    
    @staticmethod
    def _create_message(func: str, param_list: list):
        message = json.dumps({"m": func, "p": param_list}, separators=(',', ':'))
        return f"~m~{len(message)}~m~{message}"
    
    def _send_message(self, func: str, args: list):
        message = self._create_message(func, args)
        self._ws.send(message)

    def _setup_sessions(self):
        self._chart_session = self._generate_string_session("cs_")
        self._quote_session = self._generate_string_session("qs_")

        self._send_message("set_auth_token", ["unauthorized_user_token"])
        self._send_message("chart_create_session", [self._chart_session, ""])
        self._send_message("quote_create_session", [self._quote_session])
        self._send_message("quote_set_fields", [self._quote_session])

    def _request_historical_data(self, symbol: str, timeframe: Timeframe = Timeframe.H1):
        """
        Отпраявляет сообщения для получения исторических данных.
        """
        symbol_string = "=" + json.dumps({"symbol": f"BYBIT:{symbol}"})

        self._send_message("resolve_symbol", [self._chart_session, f"sds_sym_{self._i}", symbol_string])

        if self._i > 1:
            self._send_message(
                "modify_series", 
                [self._chart_session, "sds_1", f"s{self._i}", f"sds_sym_{self._i}", timeframe.value, ""]
            )
        else:
            self._send_message(
                "create_series", 
                [self._chart_session, "sds_1", "s1", "sds_sym_1", timeframe.value, 300, ""]
            )

    def _wait_for_historical_data(self, symbol: str) -> list[dict] | None:
        """
        Ожидает получение исторических данных от сервера TradingView.
        """
        timeout = 3
        start = time.time()

        while time.time() - start < timeout:
            result = self._ws.recv()
            data = re.split(r"~m~\d+~m~", result)

            try:
                data = [json.loads(part) for part in data if part]
            except json.JSONDecodeError:
                continue

            for msg in data:
                if msg.get("m") != "timescale_update":
                    continue

                series_dict = msg["p"][1]
                for series_data in series_dict.values():
                    if series_data.get("s"):
                        logger.info(f"({self._i_total}) Ценовые данные успешно получены: {symbol}")
                        return series_data.get("s")
                    
        logger.warning(f"Не удалось получить ценовые данные: {symbol}")
        return None

    @staticmethod
    def _extract_price_bars(s_list: list[dict]) -> list[TOHLC]:
        """
        Преобразует сырые данные TradingView в список TOHLC баров.
        """
        ohlc: list[TOHLC] = [
            {
                "timestamp": int(item["v"][0]),
                "open": float(item["v"][1]),
                "high": float(item["v"][2]),
                "low": float(item["v"][3]),
                "close": float(item["v"][4])
            }
            for item in s_list
        ]

        return ohlc


if __name__ == "__main__":
    with TradingViewWebSocket() as ws:
        symbols = ["BTCUSDT.P", "ETHUSDT.P", "SOLUSDT.P", "HYPEUSDT.P"]
        for symbol in symbols:
            ohlc = ws.get_historical_bars(symbol)
            with open(f"{symbol}.json", "w", encoding="utf-8") as f:
                json.dump(ohlc, f, indent=4, ensure_ascii=False)
