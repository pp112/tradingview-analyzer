import time

from data.market_data import MarketDataClient
from config import setup_logging


def main():
    setup_logging()
    market_client = MarketDataClient()
    start = time.time()
    data = market_client.get_all_historical_ohlc()
    print(f"Затрачено: {time.time() - start}")


if __name__ == "__main__":
    main()