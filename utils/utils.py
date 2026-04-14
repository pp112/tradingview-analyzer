from typing import Literal
import pandas as pd
from data.websocket_client import Timeframe


def load_data(timeframe: Timeframe) -> pd.DataFrame:
    data_path = f"data/results/historical_data_{timeframe.value}.parquet"
    return pd.read_parquet(data_path)

def get_periods_ema_sma(timeframe: Timeframe) -> tuple[int, int]:
    periods = {
        Timeframe.M15: (9, 21),
        Timeframe.M30: (12, 50),
        Timeframe.H1: (21, 50),
        Timeframe.H4: (21, 100),
        Timeframe.D1: (50, 200),
    }
    return periods.get(timeframe)

def get_symbol_df(symbol: str, df: pd.DataFrame) -> pd.DataFrame:
    return df[df["symbol"] == symbol]

def sort_correlations(tickers_correlations: dict, sort_order: Literal["asc", "desc"]):
    return dict(
        sorted(
            tickers_correlations.items(),
            key=lambda item: item[1],
            reverse=(sort_order == "desc")
        )
    )
    
def filter_low_correlations(tickers_correlations: dict, threshold: float):
    return {
        ticker: corr 
        for ticker, corr in tickers_correlations.items() 
        if corr <= threshold
    }