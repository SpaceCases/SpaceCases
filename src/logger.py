import logging
import os
from datetime import datetime


def _init_logging() -> logging.Logger:
    # Logging directory
    os.makedirs("logs", exist_ok=True)

    # Create logger
    logger = logging.getLogger("SpaceCases")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # File handler
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    log_filename = f"spacecases_{current_time}.log"
    file_handler = logging.FileHandler(f"logs/{log_filename}", mode="w+")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add handlers to discord logger too
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.INFO)
    discord_logger.addHandler(file_handler)
    discord_logger.addHandler(console_handler)

    logger.info("Logger initialised")
    return logger


logger = _init_logging()
