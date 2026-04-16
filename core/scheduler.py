import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.timeframe import Timeframe
from core.update_timeframe import TimeframeUpdater

logger = logging.getLogger(__name__)


class Scheduler:
    """
    Планировщик:
    - следит за временем обновлений
    - запускает задачи обновлений
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.updater = TimeframeUpdater()

    def start(self):
        logger.info("Запуск планировщика...")

        self.scheduler.add_job(self._run_update, "cron", minute="*/15", args=[Timeframe.M15])
        self.scheduler.add_job(self._run_update, "cron", minute="*/30", args=[Timeframe.M30])
        self.scheduler.add_job(self._run_update, "cron", minute=0, args=[Timeframe.H1])
        self.scheduler.add_job(self._run_update, "cron", hour="*/4", minute=0, args=[Timeframe.H4])
        self.scheduler.add_job(self._run_update, "cron", hour=0, minute=0, args=[Timeframe.D1])

        self.scheduler.start()
        logger.info("Планировщик успешно запущен. Контроль передан ему.")

    async def _run_update(self, timeframe: Timeframe):
        logger.info(f"SCHEDULER: Обновление {timeframe.value}")
        await self.updater.update(timeframe)

    def shutdown(self):
        logger.info("Остановка планировщика...")
        self.scheduler.shutdown(wait=False)