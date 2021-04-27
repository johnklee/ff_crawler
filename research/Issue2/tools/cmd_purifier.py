#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


r'''
This toolkit is used to wget the URL and then use purifier to do text extraction on the obtained HTML.
'''
import requests
import sys
import os
import logging
import coloredlogs
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))   # noqa

from purifier.text_extractor import TEAgent
from metrics.db_utils import DBAgent
from metrics.md5_pathlib import Md5Path
from common_utils import did2url


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''

LOGGER_FORMAT = "%(threadName)s/%(levelname)s: <%(pathname)s#%(lineno)s> %(message)s"
''' Format of Logger '''

LOGGER_LEVEL = 20  # CRITICAL=50; ERROR=40; WARNING=30; INFO=20; DEBUG=10
''' Message level of Logger '''

# REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
REQUEST_HEADERS = {'User-Agent': 'My research robot 0.1'}
''' Header of HTTP request to crawl page '''


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
    parser = argparse.ArgumentParser(description='Toolkit to do text extraction on given URL/HTML')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', type=str, help='URL to do text extraction')
    group.add_argument('--did', type=str, help='Retrieve HTML/URL from DB with given `did` as document id')
    parser.add_argument('--html', type=str, help='HTML page to do text extraction')
    parser.add_argument('--mime', type=str, default='text/html', help='MIME information (default:%(default)s)')
    parser.add_argument('--out', type=str, help='Output path to hold the text extraction result')
    parser.add_argument('--policy', type=str, help='Location to load in policy')
    parser.add_argument('--furl', type=str, help='Fake URL to simulate')
    parser.add_argument('--no_policy', action="store_true", help='Disable policy')
    parser.add_argument('--silence', action="store_true", help='Without displaying the text extraction result')
    parser.add_argument('--from_md5path', type=str, default=None, help='Retrieve MIME/URL/HTML from given Md5Path instead of DB. Used only with argument --did')
    parser.add_argument('--use_blekko', action="store_true", help='Show Blekko TE and only valid with argument --did so far')
    parser.add_argument('--show_link', action="store_true", help='Show extracted link information')
    return parser.parse_args()


def main():
    args = parse_args()
    url = args.url
    data = None
    mime = args.mime
    text = None

    if args.url:
        if args.html:
            if os.path.isfile(args.html):
                with open(args.html, 'r') as fh:
                    data = fh.read()
            else:
                # raise Exception('HTML page file={} does not exist!'.format(args.html))
                data = args.html
        else:
            rp = requests.get(args.url, headers=REQUEST_HEADERS)
            if rp.status_code == 200:
                data = rp.text
            else:
                raise Exception('Fail get page from URL={} with status code={}'.format(args.url, rp.status_code))

    elif args.did:
        did = args.did.split('-')[1] if args.did.startswith('cyberwatson-') else args.did
        if args.from_md5path:
            logger.info('Retrieve MIME/HTML/URL from Md5Path={}...'.format(args.from_md5path))
            cdid = 'cyberwatson-{}'.format(did)
            m5p = Md5Path(os.path.join(args.from_md5path, 'mime'))
            mime_fpath = m5p.resolve(cdid)
            with open(mime_fpath, 'r') as fh:
                mime = fh.read().strip()

            m5p = Md5Path(os.path.join(args.from_md5path, 'url'))
            url_fpath = m5p.resolve(cdid)
            with open(url_fpath, 'r') as fh:
                url = fh.read().strip()

            m5p = Md5Path(os.path.join(args.from_md5path, 'html'))
            html_fpath = m5p.resolve(cdid)
            with open(html_fpath, 'r') as fh:
                data = fh.read()
        else:
            dba = DBAgent()
            row = dba.id2r(did)
            if row is None:
                raise Exception('doc_id={} does not exist in DB!'.format(did))
            elif args.use_blekko:
                text = row[2]
            else:
                mime = row[1]
                data = row[3]
                if args.furl:
                    url = args.furl
                else:
                    url = did2url(did)

                if url is None:
                    raise Exception('doc_id={} does not exist in table `doc`!'.format(did))

    if args.use_blekko:
        logger.info('TE from Blekko:\n{}\n\n'.format(text))
    else:
        tea = TEAgent(ext_title=True)
        if args.no_policy:
            logger.info('Remove all policy...')
            for k, hdr in tea.handlers.items():
                hdr.stg_dict.clear()

        if args.policy:
            if os.path.isdir(args.policy):
                tea.load_policy(args.policy, namespace='test')
            else:
                raise Exception('Policy folder does not exist! ({})'.format(args.policy))

        logger.info('URL={}'.format(url))
        is_suc, rst, reason = tea.parse(mime, url, data, do_ext_link=True)
        if is_suc:
            text = rst['text'] if isinstance(rst, dict) else rst
            if 'title' in rst:
                logger.info('Title: {}'.format(rst['title']))

            if args.show_link:
                for key in ['all_links', 'body_a_links', 'body_txt_links']:
                    links = rst.get(key, [])
                    logger.info('{} ({:,d}): {}'.format(key, len(links), links))

            if args.silence:
                logger.info('TE is done with reason={}\n'.format(reason))
            else:
                logger.info('TE is done with reason={}:\n{}\n'.format(reason, text))
        else:
            # raise Exception('Policy folder does not exist! ({})'.format(args.policy))
            # with open('/tmp/test.html', 'w') as fw:
            #    fw.write(data)

            logger.warn('Failed with returned result:\n{}\n'.format(rst))
            raise Exception('Fail with reason:\n{}'.format(reason))

    if args.out:
        with open(args.out, 'w') as fw:
            fw.write(text)


if __name__ == '__main__':
    main()
