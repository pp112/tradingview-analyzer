from typing import Literal
import pandas as pd

from processing.indicator_service import IndicatorService
from utils import sort_correlations


class CorrelationCalculator:
    """
    Расчет корреляции между активами.
    """
    def calculate(
        self,
        df: pd.DataFrame,
        sort_order: Literal["asc", "desc"] = "desc"
    ) -> dict[str, float]:
        """
        Рассчитывает корреляции всех символов относительно BTC.
        """
        ticker_corrs: dict[str, float] = {}

        symbols = df["symbol"].unique()

        for symbol in symbols:
            corr = IndicatorService.correlation(df, symbol)

            if corr is None:
                continue

            ticker_corrs[symbol] = corr

        return sort_correlations(ticker_corrs, sort_order)