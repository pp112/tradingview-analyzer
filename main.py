import asyncio
import signal
import webbrowser

import uvicorn

from config import setup_logging, get_logger
from app.startup import StartupUpdater
from app.scheduler import Scheduler
from api.api import app as fastapi_app

logger = get_logger(__name__, "[APP]")


async def main():
    """
    Точка входа приложения:

    - настройка логирования
    - запуск стартового обновления данных
    - запуск планировщика
    - ожидание завершения (SIGINT/SIGTERM)
    """
    setup_logging()

    logger.info("--------------------------------------------------")
    logger.info("Запуск приложения")

    stop_event = asyncio.Event()

    scheduler = Scheduler()

    def shutdown():
        logger.info("Получен сигнал завершения")
        scheduler.shutdown()
        stop_event.set()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)
    
    host = "127.0.0.1" 
    port = 8000
    url = f"http://{host}:{port}"

    config = uvicorn.Config(
        fastapi_app, host=host, port=port, log_level="warning", log_config=None
    )
    server = uvicorn.Server(config)

    asyncio.create_task(server.serve())
    logger.info(f"Запуск веб-интерфейса: {url}")

    def open_browser():
        webbrowser.open(url)

    loop.call_later(1, open_browser)

    startup_updater = StartupUpdater()
    await startup_updater.run()

    scheduler.start()

    logger.info("Приложение запущено и работает")

    await stop_event.wait()

    logger.info("Приложение завершено корректно.")


if __name__ == "__main__":
    asyncio.run(main())