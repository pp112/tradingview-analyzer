import random
import string
import json
import re
from enum import Enum
from typing import TypedDict
from websocket import create_connection


class Timeframe(Enum):
    M30 = "30"
    H1 = "60"
    H4 = "240"
    D1 = "1D"


class OHLC(TypedDict):
    open: float
    high: float
    low: float
    close: float


class TradingViewWebSocket:
    def __init__(self):
        self.ws = None
        self.chart_session = None
        self.quote_session = None

    def __enter__(self):
        self._connect()
        self._setup_sessions()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.ws.close()
        return False

    def get_historical_bars(
        self,
        symbol: str = "BTCUSDT",
        timeframe: Timeframe = Timeframe.H1
    ) -> list[OHLC] | None:
        
        self._request_historical_data(symbol, timeframe)
        msg = self._wait_for_historical_data()
        if not msg:
            return None
        ohlc = self._extract_price_bars(msg)
        return ohlc

    def _connect(self):
        headers = {
            'Connection': 'Upgrade',
            'Host': 'data.tradingview.com',
            'Origin': 'https://data.tradingview.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56',
            'Upgrade': 'websocket'
        }

        self.ws = create_connection("wss://data.tradingview.com/socket.io/websocket", headers=headers)

    @staticmethod
    def _generate_id(prefix):
        random_string = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))
        return prefix + random_string
    
    def _generate_chart_session(self):
        return self._generate_id("cs_")
    
    def _generate_quote_session(self):
        return self._generate_id("qs_")
    
    @staticmethod
    def _create_message(func: str, param_list: list):
        message = json.dumps({"m": func, "p": param_list}, separators=(',', ':'))
        return f"~m~{len(message)}~m~{message}"
    
    def _send_message(self, func: str, args: list):
        message = self._create_message(func, args)
        self.ws.send(message)

    def _setup_sessions(self):
        self.chart_session = self._generate_chart_session()
        self.quote_session = self._generate_quote_session()

        self._send_message("set_auth_token", ["unauthorized_user_token"])
        self._send_message("chart_create_session", [self.chart_session, ""])
        self._send_message("quote_create_session", [self.quote_session])
        self._send_message("quote_set_fields", [self.quote_session])

    def _request_historical_data(self, symbol: str, timeframe: Timeframe = Timeframe.H1):
        symbol_string = "=" + json.dumps({"symbol": f"BYBIT:{symbol}"})

        self._send_message("resolve_symbol", [self.chart_session, "sds_sym_1", symbol_string])
        self._send_message("create_series", [self.chart_session, "sds_1", "s1", "sds_sym_1", timeframe.value, 300, ""])
        self._send_message("quote_add_symbols", [self.quote_session, f"BYBIT:{symbol}"])

    def _wait_for_historical_data(self) -> dict | None:
        max_attempts = 6

        for _ in range(max_attempts):
            result = self.ws.recv()
            data = re.split(r"~m~\d+~m~", result)

            data = [json.loads(part) for part in data if part]

            for msg in data:
                if msg.get("m") == "timescale_update":
                    return msg
        return None

    @staticmethod
    def _extract_price_bars(msg: dict) -> list[OHLC] | None:
        series_dict = msg["p"][1]

        for series_data in series_dict.values():
            s_list = series_data.get("s", [])

            ohlc: list[OHLC] = [
                {
                    "open": float(item["v"][1]),
                    "high": float(item["v"][2]),
                    "low": float(item["v"][3]),
                    "close": float(item["v"][4])
                }
                for item in s_list
            ]

            if ohlc:
                return ohlc
        return None

with TradingViewWebSocket() as ws:
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "HYPEUSDT"]
    for symbol in symbols:
        ohlc = ws.get_historical_bars(symbol)
        with open(f"{symbol}.json", "w", encoding="utf-8") as f:
            json.dump(ohlc, f, indent=4, ensure_ascii=False)

