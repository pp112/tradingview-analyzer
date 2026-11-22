from pathlib import Path

DATA_DIR = Path("backend/data")

HISTORICAL_DATA_DIR = DATA_DIR / "historical_data"
STATE_FILE = DATA_DIR / "state" / "last_updates.json"

VALUES_DIR = DATA_DIR / "values"
INDICATORS_DIR = VALUES_DIR / "indicators"
SIGNALS_DIR = VALUES_DIR / "signals"
CORRELATIONS_FILE = VALUES_DIR / "correlations" / "correlations.json"
LINKED_VALUES_FILE = VALUES_DIR / "linked_values" / "linked_values.json"
PRICE_VOLUME_FILE = VALUES_DIR / "price_vol_changes" / "price_vol_changes.json"


def historical_data_file(timeframe_label: str, suffix: str) -> Path:
    return HISTORICAL_DATA_DIR / f"historical_data_{timeframe_label}.{suffix}"


def indicators_file(timeframe_label: str) -> Path:
    return INDICATORS_DIR / f"values_{timeframe_label}.json"


def signals_file(timeframe_label: str) -> Path:
    return SIGNALS_DIR / f"signals_{timeframe_label}.json"