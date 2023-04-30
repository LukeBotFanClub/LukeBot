import logging
import sys

from .settings import bot_settings


def initialise_logger():
    handlers = [
        logging.StreamHandler(sys.stdout),
    ]
    if bot_settings.LOG_FILEPATH is not None:
        handlers.append(logging.FileHandler(bot_settings.LOG_FILEPATH))

    logging.basicConfig(
        level=bot_settings.LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers,
    )
    logger = logging.getLogger(__name__)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.error(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception
