import os
import logging
import logging.config
from datetime import datetime

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": f"logs/{datetime.now().strftime('%Y-%m-%d')}.log",
            "formatter": "default",
        },
    },
    "loggers": {
        "": {
            "handlers": ["file"],
            "level": "INFO",
        },
    },
}


def configure_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    return logger


logger = configure_logging()


def get_logger(name: str):
    return logging.getLogger(name)
