import logging


def _init_logging() -> logging.Logger:
    # Create logger
    logger = logging.getLogger("SpaceCases")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add handlers to discord logger too
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.INFO)
    discord_logger.addHandler(console_handler)

    logger.info("Logger initialised")
    return logger


logger = _init_logging()
