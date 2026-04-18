from dataclasses import dataclass
from typing import Literal

import yaml


@dataclass(frozen=True)
class CorrelationSettings:
    threshold: float
    sort_order: Literal["asc", "desc"]


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
    threshold = float(c.get("threshold", 0.5))
    raw_order = str(c.get("sort_order", "desc")).lower()
    sort_order = (raw_order if raw_order in ("asc", "desc") else "desc")

    correlation = CorrelationSettings(threshold=threshold, sort_order=sort_order)
    return Settings(correlation=correlation)
