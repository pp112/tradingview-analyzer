import json
from pathlib import Path
from datetime import datetime, timedelta

from models import Timeframe
from config import get_logger

logger = get_logger(__name__, "[STATE]")


class StateManager:
    """
    Управляет состоянием обновлений таймфреймов.

    Хранит время последнего обновления и определяет,
    какие таймфреймы требуют обновления.
    """
    STATE_FILE = Path("data/state/last_updates.json")
    SIGNALS_DIR = Path("data/values/signals")
    PRICE_VOL_CHANGES_FILE = Path("data/values/price_vol_changes/price_vol_changes.json")

    TIMEFRAME_INTERVALS = {
        Timeframe.H1: timedelta(hours=1),
        Timeframe.M30: timedelta(minutes=30),
        Timeframe.M15: timedelta(minutes=15),
        Timeframe.H4: timedelta(hours=4),
        Timeframe.D1: timedelta(days=1)
    }

    def __init__(self):
        self.state = self._load_state()

    def resolve_timeframes_to_update(self) -> list[Timeframe]:
        """
        Возвращает список таймфреймов, которые требуют обновления.
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
        Обновляет время последнего обновления таймфрейма.
        """
        now = datetime.now().replace(second=0, microsecond=0)
        self.state[timeframe.value] = now.isoformat()
        self._save_state()

        logger.info(f"Сохранено время обновления таймфрейма {timeframe.label}: {now}")

    def cleanup_stale_signals(self):
        """
        Удаляет файлы сигналов и price_changes, если их данные устарели.
        Вызывается при старте до запуска сервера.
        """
        now = datetime.now()

        for tf, interval in self.TIMEFRAME_INTERVALS.items():
            signal_file = self.SIGNALS_DIR / f"signals_{tf.label}.json"

            if not signal_file.exists():
                continue

            last_update = self._get_last_update(tf)
            is_stale = last_update is None or (now - last_update) >= interval

            if is_stale:
                signal_file.unlink()
                logger.info(f"Удалён устаревший файл сигналов: {tf.label}")

        if self.PRICE_VOL_CHANGES_FILE.exists():
            last_update = self._get_last_update(Timeframe.M30)
            m30_interval = self.TIMEFRAME_INTERVALS.get(Timeframe.M30)

            is_stale = last_update is None or (now - last_update) >= m30_interval
            if is_stale:
                self.PRICE_VOL_CHANGES_FILE.unlink()
                logger.info("Удалён устаревший файл изменений цен и объёмов")

    def _load_state(self) -> dict:
        if not self.STATE_FILE.exists():
            return {}
        with self.STATE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save_state(self):
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with self.STATE_FILE.open("w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    def _get_last_update(self, timeframe: Timeframe) -> datetime | None:
        value = self.state.get(timeframe.value)
        if not value:
            return None

        return datetime.fromisoformat(value)
