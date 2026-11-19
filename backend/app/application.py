import asyncio
import signal

import uvicorn

from backend.config import setup_logging, get_logger, console
from backend.app.startup import StartupUpdater
from backend.app.scheduler import Scheduler
from backend.api.api import app as fastapi_app, broadcast
from backend.exchange_portfolio.service import PortfolioService
from backend.exchanges.base import ExchangeApiError
from backend.exchanges.client_factory import create_bybit_client
from backend.storage.database import init_db

logger = get_logger(__name__, "[APP]")


class App:
    """
    Основной класс приложения.

    Управляет жизненным циклом:
    - запуск веб-сервера
    - стартовое обновление данных
    - запуск планировщика
    - корректное завершение по сигналу
    """

    HOST = "localhost"
    PORT = 8000

    def __init__(self):
        client = create_bybit_client()
        portfolio_service = PortfolioService(
            client, 
            on_updated=lambda: broadcast({"type": "portfolio"}),
        )

        fastapi_app.state.exchange_client = client
        fastapi_app.state.portfolio_service = portfolio_service

        self.portfolio_service = portfolio_service
        self.startup_updater = StartupUpdater(client)
        self.scheduler = Scheduler(client, portfolio_service)
        self.stop_event = asyncio.Event()

        config = uvicorn.Config(fastapi_app, host=self.HOST, port=self.PORT, log_level="warning", log_config=None)
        self.server = uvicorn.Server(config)
    
    async def start(self):
        """
        Запускает приложение и ожидает сигнала завершения.
        """
        setup_logging()
        init_db()
        console.print("[bold cyan]──────────────── Запуск приложения ────────────────[/bold cyan]")

        self._setup_signal_handlers()
        await self._start_server()
        await self._sync_portfolio()
        await self._run_startup()
        self._start_scheduler()

        logger.info("Приложение запущено и работает")
        await self.stop_event.wait()
        logger.info("Приложение завершено корректно.")

    async def _start_server(self):
        """
        Запускает uvicorn сервер.
        """
        asyncio.create_task(self.server.serve())
        logger.info(f"Запуск веб-интерфейса: http://{self.HOST}:{self.PORT}")

    async def _sync_portfolio(self):
        try:
            await self.portfolio_service.sync()
        except ExchangeApiError as e:
            logger.warning(f"Не удалось загрузить портфель при старте: {e}")

    async def _run_startup(self):
        """
        Выполняет стартовое обновление данных.
        """
        await self.startup_updater.run()

    def _start_scheduler(self):
        """
        Запускает планировщик обновлений данных.
        """
        self.scheduler.start()

    def _setup_signal_handlers(self):
        """
        Регистрирует обработчики сигналов SIGINT и SIGTERM для корректного завершения.
        """
        loop = asyncio.get_running_loop()
        try:
            loop.add_signal_handler(signal.SIGINT,  self._shutdown)
            loop.add_signal_handler(signal.SIGTERM, self._shutdown)
        except:
            pass

    def _shutdown(self):
        """
        Останавливает планировщик и сервер, завершает event loop.
        """
        logger.info("Получен сигнал завершения")
        self.scheduler.shutdown()
        self.server.should_exit = True
        self.stop_event.set()