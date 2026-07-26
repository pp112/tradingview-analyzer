import pandas as pd

from backend.processing.indicator_service import IndicatorService


class CorrelationCalculator:
    """
    Расчет корреляции между активами.
    """
    def calculate(self, symbol_df: pd.DataFrame) -> dict[str, float]:
        """
        Рассчитывает корреляции всех символов относительно BTC.
        """
        ticker_corrs: dict[str, float] = {}

        symbols = symbol_df["symbol"].unique()

        for symbol in symbols:
            corr = IndicatorService.correlation(symbol_df, symbol)

            if corr is None:
                continue

            ticker_corrs[symbol] = corr

        return ticker_corrs
