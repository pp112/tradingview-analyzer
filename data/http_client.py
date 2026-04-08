import json
import requests
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(message)s"
)


class TradingViewHttpClient:
    """
    Класс для получения всех тикеров с биржи ByBit, которые есть на TradingView
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

    def get_all_tickers(self) -> list[str]:

        url = "https://scanner.tradingview.com/crypto/scan?label-product=popup-screener-crypto-cex"

        response = requests.post(url=url, headers=self.headers, json=self.payload)
        response.raise_for_status()
        data_response = response.json()
        
        all_tickers = [
            d.get("s").split(":")[1] 
            for d in data_response["data"]
        ]

        logger.info(f"Успешно получено тикеров: {len(all_tickers)}")
        return all_tickers


if __name__ == "__main__":
    print(TradingViewHttpClient().get_all_tickers())