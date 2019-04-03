import logging
import os

DEFAULT_LOGGING_LEVEL = logging.DEBUG


def create_logger(level=None):
    level = level if level else DEFAULT_LOGGING_LEVEL
    logger = logging.getLogger(os.path.basename(__file__))
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
