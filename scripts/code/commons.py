"""This module has common functions which are used
throughout the library"""
#pylint: disable-msg = too-many-locals
#pylint: disable-msg = too-many-nested-blocks
#pylint: disable-msg = too-many-branches
#pylint: disable-msg = too-many-statements
import logging
import datetime
import time
import re
def logger_fetch(level=None):
    """Initialization of Logger, which can be used by all functions"""
    logger = logging.getLogger(__name__)
    default_log_level = "debug"
    if not level:
        level = default_log_level

    log_format = ('%(asctime)s:[%(name)s|%(module)s|%(funcName)s'
                  '|%(lineno)s|%(levelname)s]: %(message)s')
    if level:
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % level)
        logger.setLevel(numeric_level)
    console_logger = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    console_logger.setFormatter(formatter)
    logger.addHandler(console_logger)
    return logger
