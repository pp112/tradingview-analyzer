import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import get_logger
from models import Timeframe
from app.updater import Updater

logger = get_logger(__name__, "[SCHED]")


class Scheduler:
    """
    Асинхронный планировщик задач обновления данных:
    - следит за временем обновлений
    - запускает задачи обновлений
    """
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.updater = Updater()
        self._lock = asyncio.Lock()

    def start(self):
        logger.info("Запуск планировщика")

        self.scheduler.add_job(self._run_update, "cron", minute="1,16,31,46", args=[Timeframe.M15])
        self.scheduler.add_job(self._run_update, "cron", minute="1,31", args=[Timeframe.M30])
        self.scheduler.add_job(self._run_update, "cron", minute=1, args=[Timeframe.H1])
        self.scheduler.add_job(self._run_update, "cron", hour="*/4", minute=1, args=[Timeframe.H4])
        self.scheduler.add_job(self._run_update, "cron", hour=0, minute=1, args=[Timeframe.D1])

        self.scheduler.start()
        logger.info("Планировщик успешно запущен. Контроль передан.")

    async def _run_update(self, timeframe: Timeframe):
        """
        Запускает обновление данных для заданного таймфрейма.
        Вызывается планировщиком.
        """
        async with self._lock:
            logger.info(f"{timeframe.label}: Обновление")
            await self.updater.update_timeframe(timeframe)

    def shutdown(self):
        if self.scheduler.running:
            logger.info("Остановка планировщика")
            self.scheduler.shutdown(wait=False)