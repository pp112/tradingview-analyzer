from dataclasses import asdict, is_dataclass
import json
import threading
from pathlib import Path
from uuid import uuid4

import pandas as pd

from backend.models import Timeframe, Signal
from backend.models.linked_values import CurrentIndicatorValue
from backend.models.price_volume import PriceVolume
from backend.storage.paths import (
    CORRELATIONS_FILE, 
    HISTORICAL_DATA_DIR,
    LINKED_VALUES_FILE,
    PRICE_VOLUME_FILE, 
    historical_data_file, 
    indicators_file, 
    signals_file,
)


def ensure_dir(path: Path | str):
    """Создаёт директорию, если она не существует."""
    Path(path).mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default=None):
    """Читает JSON; если файла нет, возвращает default."""
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path | str, data, *, default=None):
    """
    Атомарно записывает данные в JSON: сначала во временный файл, потом
    подменяет им целевой, чтобы читатель не увидел наполовину записанный файл.
    """
    path = Path(path)
    ensure_dir(path.parent)
    tmp = path.with_name(f"{path.name}.{uuid4().hex}.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=default)
    tmp.replace(path)


def save_market_data(df: pd.DataFrame, timeframe: Timeframe):
    """Сохраняет исторические данные свечей в parquet и json."""
    ensure_dir(HISTORICAL_DATA_DIR)
    df.to_parquet(historical_data_file(timeframe.label, "parquet"), engine="pyarrow")
    _save_json_async(historical_data_file(timeframe.label, "json"), df)


def save_indicators(indicators: dict[str, dict], timeframe: Timeframe):
    """Сохраняет рассчитанные значения индикаторов в json."""
    write_json(indicators_file(timeframe.label), indicators, default=_json_default)


def save_signals(signals: list[Signal], timeframe: Timeframe):
    """Сохраняет торговые сигналы в json."""
    json_signals = [s.model_dump(mode="json") for s in signals]
    write_json(signals_file(timeframe.label), json_signals)


def save_correlations(correlations: dict[str, float]):
    """Сохраняет корреляции активов в json."""
    write_json(CORRELATIONS_FILE, correlations)


def save_linked_values(values: list[CurrentIndicatorValue], timeframe: Timeframe):
    """Сохраняет текущие значения индикаторов для привязанных сигналов в json."""
    data = read_json(LINKED_VALUES_FILE, default={})
    data[timeframe.label] = [v.model_dump(mode="json") for v in values]
    write_json(LINKED_VALUES_FILE, data)


def save_price_volume_changes(changes: list[PriceVolume]):
    """Сохраняет изменения цен и объёмов в json."""
    json_changes = [c.model_dump(mode="json") for c in changes]
    write_json(PRICE_VOLUME_FILE, json_changes)


def _json_default(value):
    """Сериализует dataclass-объекты в dict."""
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


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
    """Запускает task() в отдельном потоке."""
    def task():
        payload = _market_df_to_json_by_symbol(df)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)
    threading.Thread(target=task, daemon=True).start()