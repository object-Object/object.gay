import logging
import logging.config

logger = logging.getLogger(__name__)


def setup_logging():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s [%(module)s] %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "object_gay": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": True,
            },
        },
    }
    logging.config.dictConfig(config)
    logger.info("Initialized logger.")
