from config import get_logger
from storage.state_manager import StateManager
from app.updater import TimeframeUpdater

logger = get_logger(__name__, "STARTUP")


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

        if not timeframes_to_update:
            logger.info("Все таймфреймы актуальны, обновление не требуется")

        for tf in timeframes_to_update:
            await self.updater.update(tf)
            self.state_manager.set_updated(tf)

        logger.info("Стартовое обновление завершено. Все данные актуальны.")

