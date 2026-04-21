import os
import json
import threading

import pandas as pd

from models.timeframe import Timeframe
from models.sort_mode import SortMode

BASE_PATH = "data"


def ensure_dir(path: str):
    """
    Создаёт директорию, если она не существует.
    """
    os.makedirs(path, exist_ok=True)


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
    Сохраняет исторические рыночные данные (TOHLCV) в parquet и json.
    """
    path = f"{BASE_PATH}/historical_data"
    ensure_dir(path)

    filename = f"historical_data_{timeframe.label}"

    df.to_parquet(f"{path}/{filename}.parquet", engine="pyarrow")

    _save_json_async(path=f"{path}/{filename}.json", df=df)


def save_indicators(
    indicators: dict[str, dict],
    timeframe: Timeframe
):
    """
    Сохраняет рассчитанные значения индикаторов в json.
    """
    path = f"{BASE_PATH}/values/indicators"
    ensure_dir(path)

    file_path = f"{path}/values_{timeframe.label}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(indicators, f, indent=4, ensure_ascii=False)


def save_signals(
    signals: list[dict],
    timeframe: Timeframe
):
    """
    Сохраняет торговые сигналы в json.
    """
    path = f"{BASE_PATH}/values/signals"
    ensure_dir(path)

    file_path = f"{path}/signals_{timeframe.label}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=4, ensure_ascii=False)


def save_correlations(correlations: dict[str, float]):
    """
    Сохраняет корреляции активов в json.
    """
    path = f"{BASE_PATH}/values/correlations"
    ensure_dir(path)

    file_path = f"{path}/correlations.json"

    with open(file_path, "w", encoding="utf-8") as f:
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
    base_path = f"{BASE_PATH}/reports/{group}/{timeframe.label}"
    ensure_dir(base_path)

    file_path = f"{base_path}/{sort_mode.filename}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")