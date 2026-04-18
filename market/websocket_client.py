import random
import string
import json
import re
import logging
import asyncio
from models.timeframe import Timeframe
from models.tohlc import TOHLC

import websockets

logger = logging.getLogger(__name__)


class TradingViewWebSocket:
    """
    WebSocket клиент TradingView.

    Используется для получения исторических TOHLC данных.
    """
    def __init__(self):
        self._ws = None
        self._chart_session = None
        self._quote_session = None
        self._i = 1

    async def __aenter__(self):
        await self._connect()
        await self._setup_sessions()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._ws.close()

    async def get_historical_batch(
        self,
        f_update_progress,
        symbols: list[str],
        timeframe: Timeframe,
    ) -> dict[str, list[TOHLC]]:
        """
        Получает исторические TOHLC данные сразу для группы символов.
        """
        results = {}

        for symbol in symbols:
            data = await self._get_historical_bars(symbol, timeframe)
            if data:
                results[symbol] = data
            
            f_update_progress()

        return results
    
    async def _get_historical_bars(
        self,
        symbol: str,
        timeframe: Timeframe
    ) -> list[TOHLC] | None:
        """
        Запрашивает и получает исторические свечи для одного символа.
        """
        await self._request_historical_data(symbol, timeframe)
        result = await self._receive_historical_bars(symbol)
        
        self._i += 1
        
        return result
        
    async def _connect(self):
        """
        Устанавливает WebSocket соединение с TradingView.
        """        
        headers = {
            'Origin': 'https://data.tradingview.com',
            'User-Agent': 'Mozilla/5.0',
        }
        self._ws = await websockets.connect(
            "wss://data.tradingview.com/socket.io/websocket", 
            additional_headers=headers
        )
    
    async def _send_message(self, func: str, params: list):
        msg = json.dumps({"m": func, "p": params}, separators=(",", ":"))
        msg = f"~m~{len(msg)}~m~{msg}"
        await self._ws.send(msg)

    async def _setup_sessions(self):
        """
        Настройки сессии TradingView.
        """
        self._chart_session = TradingViewWebSocket._generate_string_session("cs_")
        self._quote_session = TradingViewWebSocket._generate_string_session("qs_")

        await self._send_message("set_auth_token", ["unauthorized_user_token"])
        await self._send_message("chart_create_session", [self._chart_session, ""])
        await self._send_message("quote_create_session", [self._quote_session])
        await self._send_message("quote_set_fields", [self._quote_session])

    async def _request_historical_data(self, symbol: str, timeframe: Timeframe):
        """
        Отпраявляет сообщения для получения исторических данных.
        """
        symbol_string = "=" + json.dumps({"symbol": f"BYBIT:{symbol}"})

        await self._send_message("resolve_symbol", [self._chart_session, f"sds_sym_{self._i}", symbol_string])

        if self._i > 1:
            await self._send_message(
                "modify_series", 
                [self._chart_session, "sds_1", f"s{self._i}", f"sds_sym_{self._i}", timeframe.value, ""]
            )
        else:
            await self._send_message(
                "create_series", 
                [self._chart_session, "sds_1", "s1", "sds_sym_1", timeframe.value, 600, ""]
            )

    async def _receive_historical_bars(self, symbol: str) -> list[dict] | None:
        """
        Ожидает и парсит ответ TradingView с историческими данными.
        """
        timeout = 2
        start = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start < timeout:
            msg = await self._ws.recv()
            data = re.split(r"~m~\d+~m~", msg)

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
                        logger.info(f"({self._i}) Ценовые данные успешно получены: {symbol}")
                        return TradingViewWebSocket._parse_price_bars(series_data["s"])
                    
        logger.warning(f"Не удалось получить ценовые данные: {symbol}")
        return None

    @staticmethod
    def _parse_price_bars(s_list: list[dict]) -> list[TOHLC]:
        """
        Преобразует сырой формат TradingView в список TOHLC свечей.
        """
        tohlc: list[TOHLC] = [
            {
                "Timestamp": int(item["v"][0]),
                "Open": float(item["v"][1]),
                "High": float(item["v"][2]),
                "Low": float(item["v"][3]),
                "Close": float(item["v"][4]),
                "Volume": float(item["v"][5])
            }
            for item in s_list
        ]

        return tohlc
    
    @staticmethod
    def _generate_string_session(prefix: str) -> str:
        random_string = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))
        return prefix + random_string


if __name__ == "__main__":
    with TradingViewWebSocket() as ws:
        symbols = ["BTCUSDT.P", "ETHUSDT.P", "SOLUSDT.P", "HYPEUSDT.P"]
        for symbol in symbols:
            tohlc = ws.get_historical_bars(symbol)
            with open(f"{symbol}.json", "w", encoding="utf-8") as f:
                json.dump(tohlc, f, indent=4, ensure_ascii=False)
