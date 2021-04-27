#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

r'''
This toolkit is used to dump Blekko pure text and corresponding text extraction result. (Issue13)
This toolkit will only work in ATL machine while it need to access the DB exist in ATL machine.
'''
import os
import codecs
import logging
import coloredlogs
import argparse
import queue
import time
import sys
import re
import multiprocessing
import threading
import importlib
import inspect
import shutil
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))   # noqa

from metrics.db_utils import DBAgent
from purifier.text_extractor import TEAgent
from metrics.md5_pathlib import Md5Path
from datetime import datetime
from tqdm import tqdm
from common_utils import did2url


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''

LOGGER_FORMAT = "%(threadName)s/%(levelname)s: <%(pathname)s#%(lineno)s> %(message)s"
''' Format of Logger '''

LOGGER_LEVEL = 10  # CRITICAL=50; ERROR=40; WARNING=30; INFO=20; DEBUG=10
''' Message level of Logger '''

WDS_LOG_PATH = '/home/librah/corpus-prod-nlu-model20180921/'  # '/home/jkclee/Tasks/w4cs_doc_classifier/2017_W4CS_Issue291/doc_cache/sd/2017-11-13'
''' Corpus path '''

BLK_URL_PATH = '/data/blekko/url'
''' Md5 Path to hold URL of document for Blekko '''

SYS_CPU_COUNT = multiprocessing.cpu_count()
''' System CPU Count '''

PROC_LIMIT = -1
''' Process limit used for testing '''

OUT_DOC_ID_FILE = 'DOCID_ULIST'
''' File to hold doc_id dumping list'''

HTML_SRC_DIR = None
''' HTML source file path '''


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

logging.getLogger('psycopg2').setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

blk_url_md5p = Md5Path(BLK_URL_PATH)
''' Md5Path of Blekko to hold URL information'''


################################
# Class Definition
################################
class ThreadGrp:
    r'''
    Thread Group
    '''
    def __init__(self):
        self.threads = []

    def isAlive(self):
        for t in self.threads:
            if t.isAlive():
                return True
        return False

    def pbar(self, jq, pd, total, wait=3):
        pbar = tqdm(total=total)
        done_job = 0
        while self.isAlive():
            pc_sum = sum(list(map(lambda t: t.pc, self.threads)))
            time.sleep(wait)
            progress = pc_sum - done_job
            pbar.update(progress)
            done_job = pc_sum
            if pd.is_done:
                for thd in self.threads:
                    thd.keep_running = False

        pbar.update(total - done_job)
        pbar.close()

    def join(self, jq, pd, wait=30):
        while self.isAlive():
            # if len(jsons) % 1000 == 0:
            pc_sum = sum(list(map(lambda t: t.pc, self.threads)))
            logger.info("{:,d} document(s) left...({:,d} done)".format(jq.qsize(), pc_sum))
            time.sleep(wait)

            if pd.is_done:
                for thd in self.threads:
                    thd.keep_running = False

    def clean(self):
        self.threads = []


class QProducer(threading.Thread):
    r'''
    Producer thread
    '''
    def __init__(self, jq, limit=None, jobs=None, dtype='db', hn=None):
        r'''
        Constructor of Producer thread

        :param jq: queue to stored submited job for worker thread to retrieve
        :param limit: Maximum number of job to submit
        :param jobs: Job list. None means to retrieve job from DB (table:doc_html_text)
        :param dtype: data type (db|did)
        :param hn: Query DB with desire hostname
        '''
        super(QProducer, self).__init__(name='producer')
        self.jq = jq
        ''' Job queue '''
        self.dba = DBAgent()
        ''' DB agent'''
        self.qsize = 10000
        ''' Max queue size '''
        self.limit = limit if limit is not None else PROC_LIMIT
        ''' Process limit '''
        if jobs:
            if dtype == 'db':
                self.jobs = list(map(lambda did: self.dba.id2r(did), jobs))
            elif dtype == 'did':
                self.jobs = jobs
            else:
                raise Exception('Unknown dtype={}!'.format(dtype))
        else:
            self.jobs = None
        ''' List of doc_id as job'''
        self.is_done = False
        ''' Flag for quick stop '''
        self.qq = False
        ''' Quick quit '''
        self.pc = 0
        ''' Process count '''
        self.hn = hn
        ''' Desire Hostname '''

    def done(self):
        r'''
        Enable quick stop
        '''
        self.qq = True

    def run(self):
        self.pc = 0
        jobs = self.jobs if self.jobs else self.dba.doc_html_text_gen() if self.hn is None else self.dba.rows_with_hn_gen(self.hn)
        try:
            for row in jobs:
                self.jq.put(row)
                self.pc += 1
                if self.jq.qsize() > self.qsize:
                    time.sleep(1)

                if self.limit > 0 and self.pc >= self.limit:
                    logger.warn('Reach limit={:,d}!'.format(self.limit))
                    break

                if self.qq:
                    logger.warn('Short stop is required!')
                    break
        except:
            self.is_done = True
            logger.exception('Fail in iterating jobs!')
            raise

        self.is_done = True
        logger.debug("Queue Producer is done! ({:,d})".format(self.pc))


class WThread(threading.Thread):
    r'''
    Worker thread
    '''
    def __init__(self, name, lock, jq, handler, tg):
        super(WThread, self).__init__(name=name)
        self.lock = lock
        self.name = name
        self.jq = jq
        self.keep_running = True
        self.qq = False  # Quick quit
        self.handler = handler
        self.tg = tg
        self.pc = 0

    def done(self):
        self.keep_running = False
        self.qq = True

    def run(self):
        self.tg.threads.append(self)
        while self.keep_running:
            job = None
            try:
                while not self.jq.empty():
                    if self.qq:
                        break

                    job = self.jq.get(block=False)
                    self.handler(job)
                    self.pc += 1
                    if self.keep_running and self.jq.qsize() < 100:
                        time.sleep(10)
                    elif self.keep_running and self.jq.qsize() < 1000:
                        time.sleep(3)
            except queue.Empty:
                # logger.debug('Thread-{}: Queue is empty...'.format(self.name))
                time.sleep(20)
            except:
                logger.exception('Something wrong with job={}'.format(job))

        logger.debug('Thread={} is done!'.format(self.name))


################################
# Main
################################
def dump_tc_mp(num_proc, mqueue, blekko_dir, te_dir, html_dir, ote, ohtml, fake_url=None):
    r'''
    Dump TE of given document list by multiple process

    :param num_proc: Number of worker process
    :param mqueue: Document ID queue
    :param blekko_dir: Blekko directory
    :param te_dir: Directory to store text extraction
    :param html_dir: Directory to store HTML of document
    :param ote: True to ignore blekko pure text
    :param othml: True to dump HTML only
    :param fake_url: Fake URL to feed in parser if given
    '''
    global HTML_SRC_DIR

    te_err_dir = os.path.join(os.path.dirname(te_dir), "{}_err".format(os.path.basename(te_dir)))
    if os.path.isdir(te_err_dir):
        shutil.rmtree(te_err_dir)

    os.makedirs(te_err_dir)

    def get_html_gen():
        if HTML_SRC_DIR:
            def did2row(did):
                html_fpath = os.path.join(HTML_SRC_DIR, 'cyberwatson-{}.html'.format(did))
                if not os.path.isfile(html_fpath):
                    raise Exception('HTML file from {} does not exist!'.format(html_fpath))

                row = [None, 'text/html', '', None, None]  # doc_id, mime, doc_proc, doc_raw, url
                with open(html_fpath, 'r') as fh:
                    html = fh.read()
                    row[3] = html

                return row

        else:
            dba = DBAgent()

            def did2row(did):
                row = dba.id2r(did)
                return row

        return did2row

    def worker(mqueue, blekko_dir, te_dir, html_dir, ote, ohtml, fake_url=None):
        tea = TEAgent()
        did2row = get_html_gen()

        while not mqueue.empty():
            try:
                job = mqueue.get(block=False)
                did = int(job[0])
                if len(job) == 1:
                    url = None
                else:
                    url = job[1].strip()

                doc_name = 'cyberwatson-{}.txt'.format(did)
                row = did2row(did)
                mime = row[1]
                html = row[3]

                if fake_url is not None:
                    url = fake_url
                elif url is None:
                    url = did2url(did)

                if ohtml:
                    html_out = os.path.join(html_dir, 'cyberwatson-{}.html'.format(did))
                    with codecs.open(html_out, 'w', 'utf8') as fw:
                        fw.write(html)
                else:
                    is_suc, rst, reason = tea.parse(mime, url, html)
                    if is_suc:
                        te_out = os.path.join(te_dir, doc_name)

                        if not ote:
                            blekko_out = os.path.join(blekko_dir, doc_name)
                            html_out = os.path.join(html_dir, 'cyberwatson-{}.html'.format(did))

                            with codecs.open(blekko_out, 'w', 'utf8') as fw:
                                fw.write(row[2])

                            with codecs.open(html_out, 'w', 'utf8') as fw:
                                fw.write(html)

                        with codecs.open(te_out, 'w', 'utf8') as fw:
                            fw.write(rst['text'])

                    else:
                        logger.warn('Fail to do text extraction on doc_id={}! (url={})'.format(did, url))
                        err_out = os.path.join(te_err_dir, doc_name)
                        with codecs.open(err_out, 'w', 'utf-8') as fw:
                            fw.write(url)

            except queue.Empty:
                pass
            except:
                logger.exception('Something wrong!')
                err_out = os.path.join(te_err_dir, doc_name)
                with codecs.open(err_out, 'w', 'utf-8') as fw:
                    fw.write(url)

    pbar = tqdm(total=mqueue.qsize())
    pc = mqueue.qsize()
    proc_list = []
    for i in range(num_proc):
        p = multiprocessing.Process(target=worker, args=(mqueue, blekko_dir, te_dir, html_dir, ote, ohtml, fake_url,))
        proc_list.append(p)
        p.start()

    while not mqueue.empty():
        cs = mqueue.qsize()
        if cs < pc:
            pbar.update(pc - cs)
            pc = cs

        time.sleep(1)

    pbar.update(pc)

    for p in proc_list:
        p.join()

    pbar.close()

    if os.listdir(te_err_dir):
        fail_did_list = os.listdir(te_err_dir)
        logger.info('Failed did list ({:,d}):'.format(len(fail_did_list)))
        for f in fail_did_list:
            fp = os.path.join(te_err_dir, f)
            with open(fp, 'r') as fh:
                print("* {}: {}".format(f, fh.readline().strip()))

        print("")

    shutil.rmtree(te_err_dir)


def main():
    global PROC_LIMIT
    global HTML_SRC_DIR

    # 0) Argument parsing
    parser = argparse.ArgumentParser(description='Utility to dump text of given doc_id')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--doc_id', default=None, nargs='+', type=int, help='Document id to dump.')
    group.add_argument('--file', default=None, type=str, help='The doc_id will be extracted from the file content line by line')
    group.add_argument('--url_ptn', default=None, type=str, help='Dump document with desired URL pattern')
    group.add_argument('--policy', default=None, type=str, help='Load URL pattern from given policy module & policy name (e.g.: policy24.policy_tenable*)')
    parser.add_argument('--root', default='.', type=str, help='root path to store the dump result')
    parser.add_argument('--limit', default=None, type=int, help='Process limit')
    parser.add_argument('--ote', default=False, action='store_true', help='Only dump text extraction result')
    parser.add_argument('--hn', default=None, type=str, help='Only query row with hostname as given')
    parser.add_argument('--fake_url', default=None, type=str, help='Fake URL to simulate policy selection')
    parser.add_argument('--out_miss', default=None, type=str, help='Output miss record to given file path')
    parser.add_argument('--out_te', default='te', type=str, help='Path to hold TE result')
    parser.add_argument('--ohtml', default=False, action='store_true', help='Only dump HTML part')
    parser.add_argument('--concurrency', type=int, default=max(1, int(SYS_CPU_COUNT / 2)), help='Number of process to spawn (default:%(default)s)')
    parser.add_argument('--html_src', type=str, default=None, help='Path of folder to hold HTML source file(s)')
    parser.add_argument('--short_stop', action="store_true", help='Short stop to quick once document id collection is done')
    args = parser.parse_args()

    # 1) Initialization
    te_dir = os.path.join(args.root, args.out_te)
    html_dir = None
    blekko_dir = None
    tdir_list = [te_dir]
    if not args.ote:
        html_dir = os.path.join(args.root, 'html')
        blekko_dir = os.path.join(args.root, 'blekko')
        tdir_list.extend((html_dir, blekko_dir))

    for tdir in tdir_list:
        if not os.path.isdir(tdir):
            os.makedirs(tdir)

    if args.limit:
        PROC_LIMIT = args.limit

    if args.html_src:
        HTML_SRC_DIR = args.html_src

    # 2) Start working
    if args.doc_id is not None:
        doc_id_queue = multiprocessing.Queue()
        for did in args.doc_id:
            url = did2url(did)
            job = [did, url]
            doc_id_queue.put(job)

        dump_tc_mp(args.concurrency, doc_id_queue, blekko_dir, te_dir, html_dir, args.ote, args.ohtml, fake_url=args.fake_url)

    elif args.file:
        doc_id_queue = multiprocessing.Queue()
        pc = 0
        if os.path.isfile(args.file):
            with codecs.open(args.file, 'r', 'utf8') as fh:
                for line in fh:
                    line = line.strip()
                    items = line.split('\t')
                    if not line or line.startswith('#'):
                        continue
                    elif items[0].startswith('cyberwatson-'):
                        items[0] = items[0].split('-')[1]

                    doc_id_queue.put(items)
                    pc += 1
                    if PROC_LIMIT > 0 and pc >= PROC_LIMIT:
                        break

            dump_tc_mp(args.concurrency, doc_id_queue, blekko_dir, te_dir, html_dir, args.ote, args.ohtml)
        else:
            logger.error('Input file={} does not exist!'.format(args.file))

    elif args.url_ptn or args.policy:
        dba = DBAgent()

        if args.policy:
            items = args.policy.split('.', 1)
            policy_module_name = items[0]
            policy_name_ptn = re.compile(items[1])
            # Loading policy module
            policy_module_path = "purifier/policy/{}.py".format(policy_module_name)
            logger.info('Loading policy module from {}...'.format(policy_module_path))
            spec = importlib.util.spec_from_file_location("w4cs.test.{}".format(policy_module_name), policy_module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modu_attrs = list(map(lambda n: getattr(module, n), filter(lambda n: policy_name_ptn.match(n), dir(module))))
            url_ptn = ''
            for po in list(filter(lambda v: callable(v) and not inspect.isclass(v), modu_attrs)):
                if hasattr(po, 'url_ptn'):
                    current_uptn = po.url_ptn[2:] if po.url_ptn.startswith('r:') else po.url_ptn
                    if url_ptn:
                        url_ptn += '|{}'.format(current_uptn)
                    else:
                        url_ptn = current_uptn

            logger.warn('Dump document with URL pattern from {}: {}'.format(args.policy, url_ptn))
        else:
            url_ptn = args.url_ptn
            logger.info('Dump document with URL pattern={}'.format(url_ptn))

        doc_id_iq = queue.Queue()
        doc_id_oq = queue.Queue()
        doc_id_mq = queue.Queue()
        doc_id_dq = queue.Queue()

        # 2.1) Collecting doc(s) meet searching criterion
        def search_url_ptn(url_ptn):
            ptn = re.compile(url_ptn)

            def _match(url):
                return ptn.match(url)

            return _match

        def handler_dump_doc(dba=dba, blekko_dir=blekko_dir, te_dir=te_dir, html_dir=html_dir, ote=args.ote, ohtml=args.ohtml, oqueue=doc_id_dq):
            # tea = TEAgent()

            def _handle(did):
                tea = TEAgent()
                try:
                    row = dba.id2r(did)
                except:
                    dba.session.rollback()
                    row = dba.id2r(did)

                mime = row[1]
                url = row[4]

                if ohtml:
                    html_out = os.path.join(html_dir, 'cyberwatson-{}.html'.format(did))
                    with codecs.open(html_out, 'w', 'utf8') as fw:
                        fw.write(row[3])
                else:
                    is_suc, rst, reason = tea.parse(mime, '', row[3])
                    if is_suc:
                        doc_name = 'cyberwatson-{}.txt'.format(did)
                        blekko_out = os.path.join(blekko_dir, doc_name)
                        te_out = os.path.join(te_dir, doc_name)
                        html_out = os.path.join(html_dir, 'cyberwatson-{}.html'.format(did))

                        if not ote:
                            with codecs.open(blekko_out, 'w', 'utf8') as fw:
                                fw.write(row[2])

                            with codecs.open(html_out, 'w', 'utf8') as fw:
                                fw.write(row[3])

                        with codecs.open(te_out, 'w', 'utf8') as fw:
                            fw.write(rst['text'])

                        oqueue.put((did, url))
                    else:
                        logger.warn('Fail to do text extraction on doc_id={}!'.format(did))

            return _handle

        def handler_look4doc(md5p=blk_url_md5p, oqueue=doc_id_oq, mqueue=doc_id_mq, matcher=search_url_ptn(url_ptn), dba=dba):
            def _handle(row):
                r'''
                row = tuple(doc_id, mime, doc_proc, doc_raw, url)
                '''
                doc_id = row[0]
                url = row[4]
                fn = 'cyberwatson-{}'.format(doc_id)
                fp = md5p.resolve(fn)
                if fp:
                    # with open(fp, 'r') as fh:
                    #    url = fh.read().strip()

                    if matcher(url):
                        oqueue.put(doc_id)
                    else:
                        mqueue.put(doc_id)
                else:
                    logger.warn('document id={} does not exist!'.format(fn))

            return _handle

        pthd = QProducer(doc_id_iq, hn=args.hn)
        ''' Producer thread '''
        lock = threading.Lock()
        ''' thread lock '''
        tg = ThreadGrp()
        ''' Thread group '''

        st = datetime.now()
        pthd.start()
        if PROC_LIMIT < 0:
            time.sleep(30)
        else:
            time.sleep(min(10, PROC_LIMIT / 1000))

        for i in range(SYS_CPU_COUNT - 1):
            wthd = WThread("W{}".format(i + 1), lock, doc_id_iq, handler_look4doc(), tg)
            wthd.start()

        # 2.1.1)  Wait for producer thread to done
        # pthd.join()

        # 2.1.2) Wait for all working thread(s) to be done
        tg.join(doc_id_iq, pthd)
        tg.clean()
        logger.info('Total {:,d}/{:,d} document being collected...({})'.format(doc_id_oq.qsize(), pthd.pc, datetime.now() - st))

        if doc_id_oq.qsize() == 0:
            logger.info('Done!')
            sys.exit(1)

        if args.short_stop:
            # 2.1.3) Output processed doc_id list into file
            with open(OUT_DOC_ID_FILE + '_SS', 'w') as fw:
                try:
                    ddoc_id_list = sorted(list(doc_id_oq.queue))
                    for doc_id in ddoc_id_list:
                        fw.write("{}\t{}\n".format(doc_id, did2url(doc_id)))
                except:
                    logger.exception('Fail in writing out dumping doc_id list!')

            logger.info('Short stop and quit now!')
            sys.exit(0)

        # 2.2) Dump text of those collected doc(s)
        st = datetime.now()

        # 2.2.1) Open threads to dump collected data
        total = doc_id_oq.qsize()
        doc_id_iq = queue.Queue()
        pthd = QProducer(doc_id_iq, jobs=list(doc_id_oq.queue), dtype='did')
        pthd.start()

        for i in range(SYS_CPU_COUNT - 1):
            wthd = WThread("W{}".format(i + 1), lock, doc_id_iq, handler_dump_doc(oqueue=doc_id_dq), tg)
            wthd.start()

        if args.short_stop:
            logger.info('Short stop and quit now!')
            sys.exit(0)

        tg.pbar(doc_id_iq, pthd, total)
        tg.clean()
        logger.info('{} document being dumped took time={}!\n'.format(doc_id_dq.qsize(), datetime.now() - st))

        # 2.2.2) Output processed doc_id list into file
        with open(OUT_DOC_ID_FILE, 'w') as fw:
            try:
                ddoc_id_list = sorted(list(doc_id_dq.queue))
                for doc_id, url in ddoc_id_list:
                    fw.write("{}\t{}\n".format(doc_id, url))
            except:
                logger.exception('Fail in writing out dumping doc_id list!')

        if args.out_miss and doc_id_mq.qsize() > 0:
            with open(args.out_miss, 'w') as fw:
                for doc_id in sorted(list(doc_id_mq.queue)):
                    url = dba.id2url(doc_id)
                    fw.write('{}\t{}\n'.format(doc_id, url))


if __name__ == '__main__':
    main()
