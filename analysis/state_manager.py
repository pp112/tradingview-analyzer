import os
import json
import logging
from datetime import datetime, timedelta

from data.timeframe import Timeframe

logger = logging.getLogger(__name__)


class StateManager:
    """
    Хранит и проверяет время последнего обновления таймфреймов.
    """

    STATE_FILE = "data/state/last_updates.json"

    TIMEFRAME_INTERVALS = {
        Timeframe.M15: timedelta(minutes=15),
        Timeframe.M30: timedelta(minutes=30),
        Timeframe.H1: timedelta(hours=1),
        Timeframe.H4: timedelta(hours=4),
        Timeframe.D1: timedelta(days=1),
    }

    def __init__(self):
        self.state = self._load_state()

    def get_timeframes_to_update(self) -> list[Timeframe]:
        """
        Возвращает список таймфреймов, которые нужно обновить.
        """
        now = datetime.now()
        to_update = []

        for tf, interval in self.TIMEFRAME_INTERVALS.items():
            last_update = self._get_last_update(tf)

            if last_update is None:
                logger.info(f"Нужно обновить {tf.label} (нет данных последнего обновления)")
                to_update.append(tf)
                continue

            delta = now - last_update

            if delta >= interval:
                pretty_delta = str(delta).split(".")[0]
                logger.info(f"Нужно обновить {tf.label} (прошло {pretty_delta})")
                
                to_update.append(tf)

        return to_update
    
    def set_updated(self, timeframe: Timeframe):
        """
        Записывает время обновления таймфрейма
        """
        now = datetime.now().replace(second=0, microsecond=0)
        self.state[timeframe.value] = now.isoformat()
        self._save_state()

        logger.info(f"Сохранено время обновления таймфрейма {timeframe.label}: {now}")

    def _load_state(self) -> dict:
        if not os.path.exists(self.STATE_FILE):
            return {}

        with open(self.STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_state(self):
        os.makedirs(os.path.dirname(self.STATE_FILE), exist_ok=True)

        with open(self.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    def _get_last_update(self, timeframe: Timeframe) -> datetime | None:
        value = self.state.get(timeframe.value)

        if not value:
            return None

        return datetime.fromisoformat(value)
