import logging

from data.market_data import MarketDataClient

logger = logging.getLogger(__name__)


class DataUpdater:
    def __init__(self):
        self.client = MarketDataClient()

    def update_timeframe(self, timeframe):
        self.client.get_all_historical_ohlc(timeframe)