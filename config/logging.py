import logging
from logging.handlers import RotatingFileHandler

from storage.writer import ensure_dir


def setup_logging():
    """
    Конфинг логирования
    """
    LOG_DIR = "logs"
    ensure_dir(LOG_DIR)

    APP_LOG_FILE = "app.log"
    INDICATOR_SERVICE_LOG_FILE = "warnings.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    console_formatter = logging.Formatter("[%(levelname)s] - %(message)s")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    app_file_handler = RotatingFileHandler(
        f"{LOG_DIR}/{APP_LOG_FILE}",
        maxBytes=5_000_000
    )
    app_file_handler.setLevel(logging.INFO)
    app_file_handler.setFormatter(file_formatter)

    indicator_service_file_handler = RotatingFileHandler(
        f"{LOG_DIR}/{INDICATOR_SERVICE_LOG_FILE}",
        mode="a",
        maxBytes=2_000_000
    )
    indicator_service_file_handler.setLevel(logging.WARNING)
    indicator_service_file_handler.setFormatter(file_formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_file_handler)

    # Логгер processing/indicator_service.py
    logger_indicator_service = logging.getLogger("processing.indicator_service")
    logger_indicator_service.addHandler(indicator_service_file_handler)
    logger_indicator_service.propagate = False

    # Отключенные логгеры
    disabled_loggers = [
        "market.market_data",
        "market.websocket_client"
    ]
    for name_logger in disabled_loggers:
        logging.getLogger(name_logger).disabled = True

    # приглушаем APScheduler
    logging.getLogger("apscheduler").setLevel(logging.WARNING)


def get_logger(name: str, prefix: str = ""):
    logger = logging.getLogger(name)
    return PrefixAdapter(logger, {"prefix": prefix})


class PrefixAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        prefix = self.extra.get("prefix", "")
        if prefix:
            msg = f"{prefix} {msg}"
        return msg, kwargs