from pathlib import Path

from config import get_logger
from storage.state_manager import StateManager
from app.updater import Updater
from models import Timeframe
from utils import load_data

logger = get_logger(__name__, "[STARTUP]")


class StartupUpdater:
    """
    Выполняет первичное обновление данных при старте приложения.

    Проверяет:
    - какие таймфреймы устарели
    - какие требуют обновления
    - выполняет их последовательное обновление
    """
    def __init__(self):
        self.state_manager = StateManager()
        self.updater = Updater()

    async def run(self):
        """
        Обновляет данные
        """
        signals_dir = Path("data/values/signals")
        has_signal_files = signals_dir.exists() and any(signals_dir.glob("signals_*.json"))

        if has_signal_files:
            logger.info("Очистка устаревших файлов сигналов")
            self.state_manager.cleanup_stale_signals()
        
        logger.info("Проверяем актуальность таймфреймов")
        timeframes_to_update = self.state_manager.resolve_timeframes_to_update()

        if not timeframes_to_update:
            logger.info("Все таймфреймы актуальны, обновление не требуется")
        else:
            logger.info("Начинаем стартовое обновление")

        for tf in timeframes_to_update:
            await self.updater.update_timeframe(tf)

        if Timeframe.M30 not in timeframes_to_update:
            df = load_data(Timeframe.M30)
            await self.updater.update_price_volume(df)

        if timeframes_to_update:
            logger.info("Стартовое обновление завершено. Все данные актуальны.")

