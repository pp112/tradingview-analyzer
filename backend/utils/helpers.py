import json
from pathlib import Path

import pandas as pd
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from backend.config.logging import console

from backend.models import Timeframe


def load_data(timeframe: Timeframe) -> pd.DataFrame:
    """
    Загружает исторические данные из parquet файла в DataFrame для указанного таймфрейма.
    """
    path = Path("backend/data/historical_data") / f"historical_data_{timeframe.label}.parquet"
    return pd.read_parquet(path)


def filter_by_symbol(symbol: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Фильтрует DataFrame по символу.
    """
    return df[df["symbol"] == symbol]


def format_display_symbol(symbol: str) -> str:
    """BTCUSDT.P → BTC/USDT"""
    return symbol.replace(".P", "").replace("USDT", "/USDT")


def create_progress() -> Progress:
    """
    Возвращает настроенный progress-bar для CLI загрузок.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TextColumn("[bright_green]{task.completed}[/bright_green]/[yellow]{task.total}[/yellow]"),
        TextColumn("[bright_green]{task.percentage:>3.0f}%[/bright_green]"),
        TimeRemainingColumn(),
        console=console
    )


def read_correlations() -> dict[str, float]:
    """
    Возвращает значения корреляций из файла.
    """
    path = Path("backend/data/values/correlations/correlations.json")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)