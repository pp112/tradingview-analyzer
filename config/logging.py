import logging

class PrefixAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        prefix = self.extra.get("prefix", "")
        if prefix:
            msg = f"{prefix} {msg}"
        return msg, kwargs


def get_logger(name: str, prefix: str = ""):
    logger = logging.getLogger(name)
    return PrefixAdapter(logger, {"prefix": prefix})


def setup_logging():
    """
    Конфинг логирования
    """
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] - %(message)s",
    )

    # Отключенные логгеры
    disabled_loggers = [
        "market.market_data",
        "market.websocket_client"
    ]
    for name_logger in disabled_loggers:
        logging.getLogger(name_logger).disabled = True
