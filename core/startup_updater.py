import logging

from analysis.state_manager import StateManager
from core.update_timeframe import TimeframeUpdater

logger = logging.getLogger(__name__)
logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] - %(message)s",
    )

class StartupUpdater:
    """
    Пайплайн начального обновление таймфреймов при запуске приложени:
    - Проверка времени последних обновлений
    - Определение таймфреймов, которые надо обновить
    - Обновление таймфреймов
    """

    def __init__(self):
        self.state_manager = StateManager()
        self.updater = TimeframeUpdater()

    def run(self):
        logger.info("Начинаем стартовое обновление...")

        timeframes_to_update = self.state_manager.get_timeframes_to_update()

        for tf in timeframes_to_update:
            self.updater.update(tf)
            self.state_manager.set_updated(tf)

        logger.info("Стартовое обновление завершено. Все данные актуальны.")

