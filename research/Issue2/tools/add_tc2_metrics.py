#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

r'''
This toolkit is used to copy text/mime/url file(s) from /data/blekko to metrics/test_ref in order to add test case
'''
import sys
import os
import logging
import coloredlogs
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))   # noqa

from metrics.md5_pathlib import Md5Path


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''

LOGGER_FORMAT = "%(threadName)s/%(levelname)s: <%(pathname)s#%(lineno)s> %(message)s"
''' Format of Logger '''

LOGGER_LEVEL = 20  # CRITICAL=50; ERROR=40; WARNING=30; INFO=20; DEBUG=10
''' Message level of Logger '''

BLEKKO_DAT_PATH = '/data/blekko'
''' Md5Path to hold Blekko data '''


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


################################
# Main
################################

def parse_args():
    parser = argparse.ArgumentParser(description='Add test case to metrics evaluation')
    parser.add_argument('tclist', metavar='document list separated with space', type=str, nargs='+',
                        help='document to be added into metrics evaluation. e.g.: cyberwatson-1234 or 1234')
    parser.add_argument('--from_md5path', type=str, default=BLEKKO_DAT_PATH,
                        help='Retrieve MIME/URL/HTML files from given Md5Path')

    return parser.parse_args()


def main():
    args = parse_args()
    md5_root_path = args.from_md5path
    pc = 0
    for did in args.tclist:
        if did.startswith('cyberwatson-'):
            did = did.split('-')[1]

        # Collect target file path(s)
        flist = []
        ftypes = ['html', 'mime', 'url']
        for t in ftypes:
            md5p = Md5Path(os.path.join(md5_root_path, t))
            fpath = md5p.resolve('cyberwatson-{}'.format(did))
            flist.append(fpath)

        # Copy document from blekko data source into metrics
        for t, fp in zip(ftypes, flist):
            md5p = Md5Path(os.path.join('metrics/test_input/', t))
            md5p.copy(fp)

        logger.info('{}...done!'.format(did))
        pc += 1

    logger.info('Total {:,d} test case(s) being added!\n\n'.format(pc))


if __name__ == '__main__':
    main()
