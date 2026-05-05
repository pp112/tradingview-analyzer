import json
import threading
from pathlib import Path

import pandas as pd

from models import Timeframe, SortMode, Signal

BASE_PATH = Path("data")


def ensure_dir(path: Path | str):
    """Создаёт директорию, если она не существует."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)


def _market_df_to_json_by_symbol(df: pd.DataFrame) -> dict[str, list[dict]]:
    """
    Группирует строки по уникальному символу: {symbol: [candle, ...]}.
    Поле symbol в каждой свече не дублируется — ключ только на верхнем уровне.
    """
    out = {}
    for symbol, group in df.groupby("symbol", sort=True):
        candles = group.drop(columns=["symbol"]).to_dict(orient="records")
        out[str(symbol)] = candles
    return out

def _save_json_async(path: str, df: pd.DataFrame):
    """
    Запускает task() в отдельном потоке.
    """
    def task():
        payload = _market_df_to_json_by_symbol(df)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)
    threading.Thread(target=task, daemon=True).start()

def save_market_data(df: pd.DataFrame, timeframe: Timeframe):
    """
    Сохраняет исторические данные свечей в parquet и json.
    """
    path = BASE_PATH / "historical_data"
    ensure_dir(path)
    filename = f"historical_data_{timeframe.label}"
    df.to_parquet(path / f"{filename}.parquet", engine="pyarrow")
    _save_json_async(path=path / f"{filename}.json", df=df)


def save_indicators(indicators: dict[str, dict], timeframe: Timeframe):
    """
    Сохраняет рассчитанные значения индикаторов в json.
    """
    path = BASE_PATH / "values" / "indicators"
    ensure_dir(path)
    file_path = path / f"values_{timeframe.label}.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(indicators, f, indent=4, ensure_ascii=False)


def save_signals(signals: list[Signal], timeframe: Timeframe):
    """
    Сохраняет торговые сигналы в json.
    """
    path = BASE_PATH / "values" / "signals"
    ensure_dir(path)
    file_path = path / f"signals_{timeframe.label}.json"
    data = [s.model_dump(mode="json") for s in signals]
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_correlations(correlations: dict[str, float]):
    """
    Сохраняет корреляции активов в json.
    """
    path = BASE_PATH / "values" / "correlations"
    ensure_dir(path)
    file_path = path / "correlations.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(correlations, f, indent=4, ensure_ascii=False)


def save_report_txt(
    lines: list[str],
    timeframe: Timeframe,
    group: str,
    sort_mode: SortMode
):
    """
    Сохраняет текстовый отчёт сигналов.
    """
    path = BASE_PATH / "reports" / timeframe.label / group
    ensure_dir(path)
    file_path = path / f"{sort_mode.filename}.txt"
    with file_path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def write_json(path: Path | str, data: dict):
    """
    Записывает данные в JSON файл, создавая папки если необходимо.
    """
    path = Path(path)
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)