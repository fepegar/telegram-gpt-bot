import logging
from pathlib import Path

from rich.logging import RichHandler


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = RichHandler()
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def get_cache_dir() -> Path:
    cache_dir = Path.home() / ".cache" / "tgpt"
    cache_dir.mkdir(exist_ok=True, parents=True)
    return cache_dir
