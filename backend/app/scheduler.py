import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.app.schedule import UPDATE_SCHEDULE
from backend.config import get_logger
from backend.exchange_portfolio.service import PortfolioService
from backend.exchanges.base import ExchangeApiError
from backend.models import Timeframe
from backend.app.updater import Updater

logger = get_logger(__name__, "[SCHED]")


class Scheduler:
    """
    Асинхронный планировщик задач обновления данных:
    - следит за временем обновлений
    - запускает задачи обновлений
    """
    def __init__(self, updater: Updater, portfolio_service: PortfolioService):
        self.updater = updater
        self.portfolio_service = portfolio_service
        self.scheduler = AsyncIOScheduler()
        self._lock = asyncio.Lock()

    def start(self):
        logger.info("Запуск планировщика")

        for timeframe, schedule in UPDATE_SCHEDULE.items():
            self.scheduler.add_job(
                self._run_update, "cron", args=[timeframe], **schedule.cron
            )
        self.scheduler.add_job(self._run_sync_portfolio, "interval", seconds=5)

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

    async def _run_sync_portfolio(self):
        try:
            await self.portfolio_service.sync()
        except ExchangeApiError as e:
            logger.error(f"Ошибка биржи при запросе портфеля: {e}")

    def shutdown(self):
        if self.scheduler.running:
            logger.info("Остановка планировщика")
            self.scheduler.shutdown(wait=False)