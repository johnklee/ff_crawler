#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


r'''
This toolkit is used to update DB on table `doc_html_text` for any inconsistent or outdated content.
'''
import requests
import sys
import os
import logging
import coloredlogs
import codecs
import argparse
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))   # noqa
from metrics.db_utils import DBAgent
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
    # 0) Argument parsing
    parser = argparse.ArgumentParser(description='Toolkit to update DB', usage=r'''
    // Update HTML page of document id=3659278
    # python tools/update_db.py --db_did 3659278 --url http://www.bankinfosecurity.com/state-battles-data-leakage-a-3221

    // Update HTML page of document id=3659278 in file system only without updating DB
    // If URL redirection is detected, the utility will ask permission to update the URL
    # python tools/update_db.py --db_did 3659278 --ignore_db

    // Update HTML page of document id=3659278 in file system only without updating DB
    // If URL redirection is detected, the utility will update the URL automatically
    # python tools/update_db.py --db_did 3659278 --ignore_db --auto

    ''')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--db_url', type=str, help='URL as key to locate row (column `url`)')
    group.add_argument('--db_did', type=str, help='document id as key to locate row (column `doc_id`)')
    parser.add_argument('--html', type=str, help='HTML page to read and update DB')
    parser.add_argument('--pwait', type=int, default=1, help='Polite wait between crawling in second (default:%(default)s)')
    parser.add_argument('--ignore_db', default=False, action='store_true', help='Signal to ignore in updating DB')
    parser.add_argument('--auto', default=False, action='store_true', help='Signal to conduct auto-update without asking permission')
    parser.add_argument('--url', type=str, help='URL to crawl for HTML page and update DB')
    parser.add_argument('--bpath', type=str, default='/data/blekko/',
                        help='Blekko data path to update the file system. (default:%(default)s)')

    return parser.parse_args()


def url2html(url, timeout=10, wait=0):
    r'''
    Crawl page of given URL

    :param url: URL To crawl

    :return: tuple(
        has_redir(bool): True means that redirection occurred.
        url(str): Final URL
        text(str): Content of crawled result
    )
    '''
    timeout_retry = 0
    sleep_time = 5
    while True:
        try:
            if wait > 0:
                time.sleep(wait)

            resp = requests.get(url, timeout=timeout)
            if resp.status_code != 200:
                logger.error('Unexpected sc={} for URL={}!:\n{}\n'.format(resp.status_code, url, resp))
                sys.exit(1)

            if resp.history:
                logger.warn('URL={} is redirected to {}!'.format(url, resp.url))
                return (True, resp.url, resp.text)
            else:
                return (False, resp.url, resp.text)
        except requests.exceptions.Timeout:
            timeout_retry += 1
            if timeout_retry > 3:
                raise Exception('Fail in crawling URL={}'.format(url))

            logger.warn('Connection timeout! Sleep {} seconds and retry...'.format(sleep_time))
            time.sleep(sleep_time)
            sleep_time += 2


def update_fs(bpath, doc_id, html, url=None):
    fn = 'cyberwatson-{}'.format(doc_id)
    md5Path = Md5Path(os.path.join(bpath, 'html'))
    fp = md5Path.resolve(fn)
    logger.debug('Update file={}...'.format(fp))
    with codecs.open(fp, 'w', 'utf8') as fw:
        fw.write(html)

    logger.info('Update {} successfully!'.format(fp))

    if url is not None:
        md5Path = Md5Path(os.path.join(bpath, 'url'))
        fp = md5Path.resolve(fn)
        logger.debug('Update file={}...'.format(fp))
        with open(fp, 'w') as fw:
            fw.write(url)

        logger.info('Update {} successfully!'.format(fp))


def main():
    args = parse_args()
    if not os.path.isdir(args.bpath):
        logger.error('Path={} does not exist!'.format(args.bpath))
        sys.exit(1)

    did_list = []

    # 0) Get doc_id
    dba = DBAgent()
    if args.db_url:
        did_list.append(dba.url2id())

    elif args.db_did:
        if os.path.isfile(args.db_did):
            with open(args.db_did, 'r') as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        items = line.split()
                        did_list.append(items[0].strip())
        else:
            did_list.append(args.db_did)

    # Tranform cyberwatson-<doc_id> to <doc_id>
    # e.g.: cyberwatson-1234 -> 1234
    did_list = list(map(lambda e: e.split('-')[1] if e.startswith('cyberwatson-') else e, did_list))

    logger.info('Total {:,d} document to process...'.format(len(did_list)))
    pc = 0
    for doc_id in did_list:
        has_redir = False
        html = None
        dict2update = {}
        pc += 1
        # 1) Get HTML
        if args.html:
            with open(args.html, 'r') as fh:
                html = fh.read()
        elif args.url:
            has_redir, url, html = url2html(args.url, wait=args.pwait)
        else:
            url = dba.id2url(doc_id)
            logger.info('Get HTML of {} ({})...'.format(doc_id, url))
            logger.debug('doc_id={} with URL={}...'.format(doc_id, url))
            has_redir, url, html = url2html(url, wait=args.pwait)
            logger.debug('Crawled HTML({:,d})...(has_redir={})'.format(len(html), has_redir))

        dict2update['doc_raw'] = html
        if has_redir:
            if args.auto:
                dict2update['url'] = url
            else:
                while True:
                    ans = input('Has redirection! Would you like to update URL too? (y/n): ').lower()
                    if ans == 'y':
                        dict2update['url'] = url
                        break
                    elif ans == 'n':
                        break

        # 2) Update DB
        logger.info('Update DB and file system...')
        if not args.ignore_db:
            rst = dba.u_doc_html_text(doc_id, dict2update)
            if rst.rowcount == 1:
                logger.info('Updated DB successfully!')
            else:
                logger.warning('Something wrong on doc_id={}!:\n{}\n'.format(doc_id, rst))
                sys.exit(1)

        # 3) Update file system
        update_fs(args.bpath, doc_id, html, dict2update.get('url', None))


if __name__ == '__main__':
    main()
