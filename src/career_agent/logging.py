"""Logging setup. Entry points call `configure_logging()`; library code only imports `logger`."""

import sys

from loguru import logger

from career_agent.config import Settings, get_settings

_configured = False


def configure_logging(settings: Settings | None = None) -> None:
    global _configured
    if _configured:
        return
    settings = settings or get_settings()
    logger.remove()
    logger.add(sys.stdout, level=settings.log_level, format="{time} | {level} | {name} | {message}")
    if settings.log_file:
        logger.add(settings.log_file, rotation="1 MB", level=settings.log_level)
    _configured = True


__all__ = ["configure_logging", "logger"]
