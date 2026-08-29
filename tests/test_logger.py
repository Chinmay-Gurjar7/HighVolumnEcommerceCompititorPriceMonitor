import logging

from logger.logger import get_logger


def test_get_logger_returns_logger():
    logger = get_logger(
        "test_logger_returns_logger"
    )

    assert isinstance(
        logger,
        logging.Logger
    )


def test_get_logger_configures_handlers():
    logger = get_logger(
        "test_logger_handlers"
    )

    assert len(logger.handlers) == 2

    assert any(
        isinstance(handler, logging.FileHandler)
        for handler in logger.handlers
    )

    assert any(
        isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
        for handler in logger.handlers
    )


def test_get_logger_sets_log_level():
    logger = get_logger(
        "test_logger_level"
    )

    assert logger.level == logging.INFO


def test_get_logger_prevents_duplicate_handlers():
    logger = get_logger(
        "test_logger_duplicate_handlers"
    )

    first_count = len(logger.handlers)

    same_logger = get_logger(
        "test_logger_duplicate_handlers"
    )

    second_count = len(same_logger.handlers)

    assert same_logger is logger
    assert first_count == second_count == 2


def test_logger_can_log_messages():
    logger = get_logger(
        "test_logger_messages"
    )

    logger.info("Logger test started.")
    logger.warning("This is a warning.")
    logger.error("This is an error.")

    assert len(logger.handlers) == 2