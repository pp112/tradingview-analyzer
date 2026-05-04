import logging
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler
from rich.console import Console

from storage.writer import ensure_dir

console = Console()

def setup_logging():
    """
    Конфигурация логирования.
    """
    LOG_DIR = "logs"
    ensure_dir(LOG_DIR)
    
    file_formatter = logging.Formatter(
        "%(asctime)s - %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Хэндлеры ──────────────────────────────────────────────────────────────

    # Консоль
    console_handler = RichHandler(
        console=console,
        show_path=False,
        show_level=True,
        show_time=True,
        markup=True,
        rich_tracebacks=True,
        log_time_format="[%H:%M:%S]",
        omit_repeated_times=False
    )
    console_handler.setLevel(logging.INFO)

    # Файл — все INFO и выше логи приложения
    app_file_handler = RotatingFileHandler(
        f"{LOG_DIR}/app.log",
        maxBytes=5_000_000
    )
    app_file_handler.setLevel(logging.INFO)
    app_file_handler.setFormatter(file_formatter)

    # Файл — только WARNING и выше от indicator_service
    indicator_service_file_handler = RotatingFileHandler(
        f"{LOG_DIR}/warnings.log",
        mode="a",
        maxBytes=2_000_000
    )
    indicator_service_file_handler.setLevel(logging.WARNING)
    indicator_service_file_handler.setFormatter(file_formatter)

    # ── Root логгер ───────────────────────────────────────────────────────────

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_file_handler)

    # ── Отдельные логгеры ─────────────────────────────────────────────────────

    # Логгер processing/indicator_service.py
    logging.getLogger("processing.indicator_service").addHandler(indicator_service_file_handler)
    logging.getLogger("processing.indicator_service").propagate = False

    # Отключаем шумные логгеры загрузки данных
    logging.getLogger("market.market_data").disabled = True
    logging.getLogger("market.websocket_client").disabled = True

    # приглушаем APScheduler
    logging.getLogger("apscheduler").setLevel(logging.WARNING)


def get_logger(name: str, prefix: str = ""):
    logger = logging.getLogger(name)
    return PrefixAdapter(logger, {"prefix": prefix})


class PrefixAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        prefix = self.extra.get("prefix", "")
        if prefix:
            msg = f"{prefix} - {msg}"
        return msg, kwargs