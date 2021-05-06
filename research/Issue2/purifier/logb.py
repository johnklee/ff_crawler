#!/usr/bin/python3
import logging
import os
import coloredlogs


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''

LOGGER_FORMAT = "%(threadName)s/%(levelname)s: <%(pathname)s#%(lineno)s> %(message)s"
''' Format of Logger '''

LOGGER_LEVEL = 20  # CRITICAL=50; ERROR=40; WARNING=30; INFO=20; DEBUG=10
''' Message level of Logger '''


################################
# Constants
################################
def getLogger(name, level=LOGGER_LEVEL, fmt=LOGGER_FORMAT):
    if 'purifier' in logging.root.manager.loggerDict:
        return logging.getLogger('purifier')
    else:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False
        coloredlogs.install(level=level, logger=logger, fmt=fmt)
        return logger
