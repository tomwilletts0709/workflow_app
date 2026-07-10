import logging

from app.core.settings import get_settings

LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


def configure_logging() -> None:
    settings = get_settings()
    log_level = settings.log_level.upper()

    if log_level not in logging._nameToLevel:
        log_level = "WARNING"

    logging.basicConfig(
        level=logging._nameToLevel[log_level],
        format=LOG_FORMAT_DEBUG if log_level == "DEBUG" else None,
    )
