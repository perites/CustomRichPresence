import logging

logger = logging.getLogger("activity")


def set_custom_logger(custom_logger: logging.Logger):
    global logger
    logger = custom_logger
