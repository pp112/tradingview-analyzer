import json
from typing import Literal

import pandas as pd
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

from models.timeframe import Timeframe


def load_data(timeframe: Timeframe) -> pd.DataFrame:
    """
    Загружает исторические данные parquet для указанного таймфрейма.
    """
    data_path = f"data/historical_data/historical_data_{timeframe.label}.parquet"
    return pd.read_parquet(data_path)

def get_periods_ema_sma(timeframe: Timeframe) -> tuple[int, int]:
    periods = {
        Timeframe.M15: (9, 21),
        Timeframe.M30: (12, 50),
        Timeframe.H1: (21, 50),
        Timeframe.H4: (21, 100),
        Timeframe.D1: (50, 200)
    }
    return periods.get(timeframe)

def get_symbol_df(symbol: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Фильтрует DataFrame по символу.
    """
    return df[df["symbol"] == symbol]

def sort_correlations(tickers_correlations: dict, sort_order: Literal["asc", "desc"]):
    """
    Сортирует словарь корреляций по значению.
    """
    return dict(
        sorted(
            tickers_correlations.items(),
            key=lambda item: item[1],
            reverse=(sort_order == "desc")
        )
    )

def get_progress():
    """
    Возвращает настроенный progress-bar для CLI загрузок.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TextColumn("[bright_green]{task.completed}[/bright_green]/[yellow]{task.total}[/yellow]"),
        TextColumn("[bright_green]{task.percentage:>3.0f}%[/bright_green]"),
        TimeRemainingColumn()
    )

def read_correlations() -> dict[str, float]:
    """
    Возвращает значения корреляций из файла.
    """
    path_file = "data/values/correlations/correlations.json"

    with open(path_file, encoding="utf-8") as f:
        ticker_corr = json.load(f)

    return ticker_corr