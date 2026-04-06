import random
import string
import json
import re
from websocket import create_connection

class TradingViewWebSocket:
    def __init__(self):
        self.ws = None

    def connect(self):
        headers = {
            'Connection': 'Upgrade',
            'Host': 'data.tradingview.com',
            'Origin': 'https://data.tradingview.com',
            # 'Cache-Control': 'no-cache',
            # 'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            # 'Sec-WebSocket-Key': 'ojiM9JH/pIh+QJ8HyJ3JYQ==',
            # 'Sec-WebSocket-Version': '13',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56',
            # 'Pragma': 'no-cache',
            'Upgrade': 'websocket'
        }

        self.ws = create_connection("wss://data.tradingview.com/socket.io/websocket", headers=headers)

    @staticmethod
    def generate_id(prefix):
        random_string = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))
        return prefix + random_string
    
    def generate_chart_session(self):
        return self.generate_id("cs_")
    
    def generate_quote_session(self):
        return self.generate_id("qs_")
    
    @staticmethod
    def create_message(func: str, param_list: list):
        message = json.dumps({"m": func, "p": param_list}, separators=(',', ':'))
        return f"~m~{len(message)}~m~{message}"
    
    def send_message(self, func: str, args: list):
        message = self.create_message(func, args)
        self.ws.send(message)

    def run(self, symbol):
        chart_session = self.generate_chart_session()
        quote_session = self.generate_quote_session()

        self.send_message("set_auth_token", ["unauthorized_user_token"])
        self.send_message("chart_create_session", [chart_session, ""])
        self.send_message("quote_create_session", [quote_session])
        args = [
            quote_session, "base-currency-logoid", "logo", "ch", "chp"
            "currency-logoid", "currency_code", "currency_id","base_currency_id",
            "current_session", "description", "exchange", "format", "fractional",
            "is_tradable", "language", "local_description", "listed_exchange",
            "logoid", "lp", "lp_time", "minmov", "minmove2",
            "pricescale", "pro_name", "short_name", "type", "typespecs",
            "update_mode", "volume", "variable_tick_size", "value_unit_id", 
            "unit_id", "measure"
        ]
        self.send_message("quote_set_fields", args)

        symbol_data = {
            "adjustment": "splits",
            "currency-id": "XTVCUSDT",
            "session": "regular",
            "settlement-as-close": False,
            "symbol": f"BYBIT:{symbol}"
        }
        args = "=" + json.dumps(symbol_data)

        self.send_message("quote_add_symbols", [quote_session, args])

        symbol_data2 = {
            "adjustment": "splits",
            "currency-id": "XTVCUSDT",
            "metric": "price",
            "session": "regular",
            "settlement-as-close": False,
            "symbol": f"BYBIT:{symbol}"
        }

        args2 = "=" + json.dumps(symbol_data2)

        self.send_message("resolve_symbol", [chart_session, "sds_sym_1", args2])

        self.send_message("create_series", [chart_session, "sds_1", "s1", "sds_sym_1", "60", 100, ""])
        self.send_message("quote_add_symbols", [quote_session, f"BYBIT:{symbol}"])

        while True:
            result = self.ws.recv()
            data = re.split(r"~m~\d+~m~", result)
            
            messages = []
            for part in data:
                if not part:
                    continue

                messages.append(json.loads(part))
            
            if any(msg.get("m") == "series_loading" for msg in messages):
                break
            
        with open("Минимум.json", "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)


        
    def close(self):
        if self.ws:
            self.ws.close()
try:
    ws = TradingViewWebSocket()
    ws.connect()
    ws.run("BTCUSDT")
finally:
    ws.close()