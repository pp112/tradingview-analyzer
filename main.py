import asyncio
import signal

from config import setup_logging, get_logger
from app.startup import StartupUpdater
from app.scheduler import Scheduler

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

    logger.info("\nЗапуск приложения")

    stop_event = asyncio.Event()

    scheduler = Scheduler()

    def shutdown():
        logger.info("Получен сигнал завершения")
        scheduler.shutdown()
        stop_event.set()

    loop = asyncio.get_running_loop()

    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    startup_updater = StartupUpdater()
    await startup_updater.run()

    scheduler.start()

    logger.info("Приложение запущено и работает")

    await stop_event.wait()

    logger.info("Приложение завершено корректно.")


if __name__ == "__main__":
    asyncio.run(main())