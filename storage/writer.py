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
    all_data: dict[str, list[TOHLC]],
    timeframe: Timeframe
):
    """
    Сохраняет исторические рыночные данные (TOHLC) в parquet и json.
    """
    path = f"{BASE_PATH}/historical_data"
    ensure_dir(path)

    filename = f"historical_data_{timeframe.label}"

    df_list = []

    for symbol, series in all_data.items():
        df = pd.DataFrame(series)
        df["symbol"] = symbol
        df_list.append(df)

    if df_list:
        full_df = pd.concat(df_list, ignore_index=True)

        full_df.to_parquet(
            f"{path}/{filename}.parquet",
            engine="pyarrow"
        )

    with open(f"{path}/{filename}.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)


def save_indicators(
    indicators: dict[str, dict],
    timeframe: Timeframe
):
    """
    Сохраняет рассчитанные значения индикаторов в json.
    """
    path = f"{BASE_PATH}/value/indicators"
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
    path = f"{BASE_PATH}/value/signals"
    ensure_dir(path)

    file_path = f"{path}/signals_{timeframe.label}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=4, ensure_ascii=False)


def save_correlations(correlations: dict[str, float]):
    """
    Сохраняет корреляции активов в json.
    """
    path = f"{BASE_PATH}/value/correlations"
    ensure_dir(path)

    file_path = f"{path}/correlations.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(correlations, f, indent=4, ensure_ascii=False)


def save_report(
    lines: list[str],
    timeframe: Timeframe
):
    """
    Сохраняет текстовый отчёт сигналов.
    """
    path = f"{BASE_PATH}/reports"
    ensure_dir(path)

    file_path = f"{path}/signals_{timeframe.label}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")