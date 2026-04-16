import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] - %(message)s",
    )

    # Отключенные логгеры
    disabled_loggers = [
        "data.market_data",
        "data.websocket_client"
    ]
    for name_logger in disabled_loggers:
        logging.getLogger(name_logger).disabled = True
