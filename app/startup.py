import logging

from processing.state_manager import StateManager
from app.updater import TimeframeUpdater

logger = logging.getLogger(__name__)


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
        self.updater = TimeframeUpdater()

    async def run(self):
        logger.info("Начинаем стартовое обновление...")

        timeframes_to_update = self.state_manager.get_timeframes_to_update()

        for tf in timeframes_to_update:
            await self.updater.update(tf)
            self.state_manager.set_updated(tf)

        logger.info("Стартовое обновление завершено. Все данные актуальны.")

