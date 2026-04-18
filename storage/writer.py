import os
import json

import pandas as pd

from models.timeframe import Timeframe
from models.tohlc import TOHLC


BASE_PATH = "data"


def ensure_dir(path: str):
    """
    Создаёт директорию, если она не существует.
    """
    os.makedirs(path, exist_ok=True)


def save_market_data(
    df: pd.DataFrame,
    timeframe: Timeframe
):
    """
    Сохраняет исторические рыночные данные (TOHLC) в parquet и json.
    """
    path = f"{BASE_PATH}/historical_data"
    ensure_dir(path)

    filename = f"historical_data_{timeframe.label}"

    df.to_parquet(f"{path}/{filename}.parquet", engine="pyarrow")

    df.to_json(f"{path}/{filename}.json", orient="records", indent=4)


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


def save_report(
    lines: list[str],
    timeframe: Timeframe,
    suffix: str = ""
):
    """
    Сохраняет текстовый отчёт сигналов.
    """
    path = f"{BASE_PATH}/reports"
    ensure_dir(path)

    file_path = f"{path}/signals_{timeframe.label}{suffix}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")