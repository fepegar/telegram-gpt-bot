import logging

from rich.logging import RichHandler


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = RichHandler()
    logger.addHandler(handler)
    logger.propagate = False
    return logger
