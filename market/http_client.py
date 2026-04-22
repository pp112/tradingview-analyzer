import json
import aiohttp
import copy

from config import get_logger

logger = get_logger(__name__, "[HTTP]")


class TradingViewHttpClient:
    """
    HTTP клиент для получения списка доступных тикеров с TradingView.
    """

    URL = "https://scanner.tradingview.com/crypto/scan?label-product=popup-screener-crypto-cex"

    def __init__(self):
        with open("market/payloads/scanner.json", encoding="utf-8") as f:
            self.payload = json.load(f)

        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://www.tradingview.com",
            "Referer": "https://www.tradingview.com/"
        }

    async def fetch_data(self) -> dict[str, dict[str, float]]:
        """
        Возвращает список всех доступных крипто-тикеров .
        """
        data = await self._post(self.payload)
        parsed_data = self._parse_data(data)
        logger.info(f"Получено тикеров с данными: {len(parsed_data)}")
        return parsed_data

    async def _post(self, payload: dict) -> dict:
        """
        Выполняет POST-запрос к TradingView Scanner и возвращает сырой JSON.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(self.URL, headers=self.headers, json=payload) as r:
                r.raise_for_status()
                return await r.json()

    def _parse_data(self, data: dict) -> dict[str, dict[str, float]]:
        """
        Парсер json-ответа post-запроса  
        """
        result = {}
        for item in data["data"]:
            symbol_name = item["s"].split(":")[1]
            change_price = round(item["d"][0], 2)
            change_volume = round(item["d"][1], 2)
            result[symbol_name] = {
                "change_price": change_price,
                "change_volume": change_volume
            }
        return result


if __name__ == "__main__":
    import asyncio
    http_client = TradingViewHttpClient()
    result = asyncio.run(http_client.fetch_data())
    with open("market/rersponse.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
