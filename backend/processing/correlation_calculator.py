import pandas as pd

from backend.processing.indicator_service import correlation


def calculate_correlations(symbol_df: pd.DataFrame) -> dict[str, float]:
    """
    Рассчитывает корреляции всех символов относительно BTC.
    """
    ticker_corrs = {}

    symbols = symbol_df["symbol"].unique()

    for symbol in symbols:
        corr = correlation(symbol_df, symbol)
        if corr is not None:
            ticker_corrs[symbol] = corr

    return ticker_corrs
