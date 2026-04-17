import logging

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
