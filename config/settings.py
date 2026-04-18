from dataclasses import dataclass
from typing import Literal

import yaml


@dataclass(frozen=True)
class CorrelationSettings:
    corr_threshold: float
    corr_sort_order: Literal["asc", "desc"]


@dataclass(frozen=True)
class Settings:
    correlation: CorrelationSettings


def load_settings() -> Settings:
    """
    Читает настройки из config/settings.yaml.
    """
    path = "config/settings.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    c = data.get("correlation") or {}
    corr_threshold = float(c.get("corr_threshold", 0.5))
    raw_order = str(c.get("corr_sort_order", "desc")).lower()
    corr_sort_order = (raw_order if raw_order in ("asc", "desc") else "desc")

    correlation = CorrelationSettings(corr_threshold=corr_threshold, corr_sort_order=corr_sort_order)
    return Settings(correlation=correlation)
