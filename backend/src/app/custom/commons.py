"""This module has common functions which are used
throughout the library"""
import logging
import requests
import datetime
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


def get_date_object(date_string, date_format=None):
    """returns a date object from python date"""
    try:
        if date_format is not None:
            my_date = datetime.datetime.strptime(date_string, date_format).date()
        elif "/" in date_string:
            my_date = datetime.datetime.strptime(date_string, '%d/%m/%Y').date()
        else:
            my_date = datetime.datetime.strptime(date_string, '%d-%m-%Y').date()
    except:
        my_date = None
    return my_date
