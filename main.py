import asyncio
import signal
import logging

from config import setup_logging
from core.startup_updater import StartupUpdater
from core.scheduler import Scheduler

logger = logging.getLogger(__name__)


async def main():
    setup_logging()

    stop_event = asyncio.Event()

    scheduler = Scheduler()

    def shutdown():
        logger.info("Получен сигнал завершения...")
        scheduler.shutdown()
        stop_event.set()

    loop = asyncio.get_running_loop()

    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    startup_updater = StartupUpdater()
    await startup_updater.run()

    scheduler.start()

    logger.info("Приложение запущено и работает...")

    await stop_event.wait()

    logger.info("Приложение завершено корректно.")


if __name__ == "__main__":
    asyncio.run(main())