import logging
import sys

from .settings import settings


def initialise_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(settings.LOG_LEVEL)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    if settings.LOG_FILEPATH is not None:
        logger.addHandler(logging.FileHandler(settings.LOG_FILEPATH))

    def exception_handler(type_, value, tb):  # noqa: F841
        logger.exception(value)

    sys.excepthook = exception_handler
