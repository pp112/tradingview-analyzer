import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.config import get_logger
from backend.exchange_portfolio.service import PortfolioService
from backend.exchanges.base import ExchangeApiError, ExchangeClient
from backend.models import Timeframe
from backend.app.updater import Updater

logger = get_logger(__name__, "[SCHED]")


class Scheduler:
    """
    Асинхронный планировщик задач обновления данных:
    - следит за временем обновлений
    - запускает задачи обновлений
    """
    def __init__(
        self,
        client: ExchangeClient,
        portfolio_service: PortfolioService,
    ):
        self.scheduler = AsyncIOScheduler()
        self.updater = Updater(client)
        self.portfolio_service = portfolio_service
        self._lock = asyncio.Lock()

    def start(self):
        logger.info("Запуск планировщика")

        self.scheduler.add_job(self._run_update, "cron", minute="1,16,31,46", args=[Timeframe.M15])
        self.scheduler.add_job(self._run_update, "cron", minute="1,31", args=[Timeframe.M30])
        self.scheduler.add_job(self._run_update, "cron", minute=1, args=[Timeframe.H1])
        self.scheduler.add_job(self._run_update, "cron", hour="*/4", minute=1, args=[Timeframe.H4])
        self.scheduler.add_job(self._run_update, "cron", hour=0, minute=1, args=[Timeframe.D1])
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