import asyncio
import signal
import webbrowser

import uvicorn

from config import setup_logging, get_logger
from app.startup import StartupUpdater
from app.scheduler import Scheduler
from api.api import app as fastapi_app

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
        self.startup_updater = StartupUpdater()
        self.scheduler = Scheduler()
        self.stop_event = asyncio.Event()

        config = uvicorn.Config(fastapi_app, host=self.HOST, port=self.PORT, log_level="warning", log_config=None)
        self.server = uvicorn.Server(config)
    
    async def start(self):
        """
        Запускает приложение и ожидает сигнала завершения.
        """
        setup_logging()
        logger.info("--------------------------------------------------")
        logger.info("Запуск приложения")

        self._setup_signal_handlers()
        await self._start_server()
        await self._run_startup()
        self._start_scheduler()

        logger.info("Приложение запущено и работает")
        await self.stop_event.wait()
        logger.info("Приложение завершено корректно.")

    async def _start_server(self):
        """
        Запускает uvicorn сервер и открывает браузер через 1 секунду.
        """
        asyncio.create_task(self.server.serve())
        loop = asyncio.get_running_loop()

        logger.info(f"Запуск веб-интерфейса: http://{self.HOST}:{self.PORT}")
        loop.call_later(1, webbrowser.open, f"http://{self.HOST}:{self.PORT}")

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
        loop.add_signal_handler(signal.SIGINT,  self._shutdown)
        loop.add_signal_handler(signal.SIGTERM, self._shutdown)

    def _shutdown(self):
        """
        Останавливает планировщик и сервер, завершает event loop.
        """
        logger.info("Получен сигнал завершения")
        self.scheduler.shutdown()
        self.server.should_exit = True
        self.stop_event.set()