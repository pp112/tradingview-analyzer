import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] - %(message)s",
    )

    disabled_loggers = [
        "data.market_data",
        "data.websocket_client",
        "analysis.indicator_engine"
    ]

    for name_logger in disabled_loggers:
        logging.getLogger(name_logger).disabled = True