import logging
from pathlib import Path

from utils.config_manager import ConfigurationManager


def get_logger(name: str = "ecommerce_price_monitor") -> logging.Logger:
    """
    Create and return a configured project logger.

    Logs are written to:
        logs/pipeline.log

    and also displayed in the terminal.
    """

    config_manager = ConfigurationManager()
    logging_config = config_manager.get_logging_config()

    log_directory = logging_config.log_dir
    log_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    log_file = log_directory / logging_config.log_file

    logger = logging.getLogger(name)

    # Prevent duplicate handlers if get_logger()
    # is called multiple times.
    if logger.handlers:
        return logger

    log_level = getattr(
        logging,
        logging_config.level.upper(),
        logging.INFO
    )

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = logging.FileHandler(
        filename=log_file,
        encoding="utf-8"
    )

    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()

    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger