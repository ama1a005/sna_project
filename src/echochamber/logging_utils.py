"""Structured logging utilities."""

import logging
import sys
from pathlib import Path


def setup_logger(
    name: str = "echochamber",
    level: int = logging.INFO,
    log_file: Path | None = None,
) -> logging.Logger:
    """Configure and return a standardized logger with console and optional file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if setup_logger is called repeatedly
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
