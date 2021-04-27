#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

r'''
This module is used to keep shared function/API to be used by other utilities
'''
import os
import logging
import coloredlogs
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))   # noqa

from metrics.md5_pathlib import Md5Path


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''

LOGGER_FORMAT = "%(threadName)s/%(levelname)s: <%(pathname)s#%(lineno)s> %(message)s"
''' Format of Logger '''

LOGGER_LEVEL = 10  # CRITICAL=50; ERROR=40; WARNING=30; INFO=20; DEBUG=10
''' Message level of Logger '''

BLK_URL_PATH = '/data/blekko/url'
''' Md5 Path to hold URL of document for Blekko '''


################################
# Global Variables
################################
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(LOGGER_LEVEL)
logger.propagate = False
coloredlogs.install(
    level=LOGGER_LEVEL,
    logger=logger,
    fmt=LOGGER_FORMAT)
''' logger initialization '''

blk_url_md5p = Md5Path(BLK_URL_PATH)
''' Md5Path of Blekko to hold URL information'''


def did2url(doc_id):
    r'''
    Return the URL of given document id

    :param doc_id: Document ID. e.g.: 'cyberwatson-1234' or 1234

    :return:
        URL of given document id or None if not exist
    '''
    global blk_url_md5p
    if isinstance(doc_id, int) or not doc_id.startswith('cyberwatson-'):
        doc_id = 'cyberwatson-{}'.format(doc_id)

    fp = blk_url_md5p.resolve(doc_id)
    if fp:
        with open(fp, 'r') as fh:
            return fh.read().strip()
    else:
        logger.warn('doc_id={} doesn\'t exist in {}!'.format(BLK_URL_PATH))
        return None
