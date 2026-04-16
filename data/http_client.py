import json
import aiohttp
import logging

logger = logging.getLogger(__name__)


class TradingViewHttpClient:
    """
    HTTP клиент для получения списка доступных тикеров с TradingView.
    """
    def __init__(self):
        with open("data/scanner_payload.json", encoding="utf-8") as f:
            self.payload = json.load(f)

        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://www.tradingview.com",
            "Referer": "https://www.tradingview.com/"
        }

    async def get_all_tickers(self) -> list[str]:
        """
        Возвращает список всех доступных крипто-тикеров с TradingView (ByBit).
        """
        url = "https://scanner.tradingview.com/crypto/scan?label-product=popup-screener-crypto-cex"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=self.payload) as r:
                r.raise_for_status()
                data = await r.json()

        tickers = [
            d.get("s").split(":")[1] 
            for d in data["data"]
        ]

        logger.info(f"Успешно получено тикеров: {len(tickers)}")
        return tickers


if __name__ == "__main__":
    import asyncio
    tickers = asyncio.run(TradingViewHttpClient().get_all_tickers())
    print(tickers)