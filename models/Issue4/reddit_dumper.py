#!/usr/bin/env python
import pickle
import os
import time
import pathlib
import logging
import praw
import json
from logb import get_logger
from datetime import datetime
from typing import Dict
from tqdm import tqdm


ROOT_PATH = pathlib.Path(__file__).parent.absolute()
CACHE_PKL_NAME = os.path.join(ROOT_PATH, 'reddit_pulled_post_cache.pkl')
DUMP_DIR_PATH = os.path.join(ROOT_PATH, "reddit_post_dumps")
PULL_SIZE_LIMIT = 1000
logger = get_logger("issue4")

logger.info('Initializing PRAW agent...')
with open('client_secrets.json', 'r') as fo:
    reddit_credentials = json.load(fo)
    rdt_agent = praw.Reddit(**reddit_credentials)

# Create a sub-reddit object for topic we are interested in (r/GooglePixel)
st_googlepixel = rdt_agent.subreddit("GooglePixel")


def get_ts() -> int:
    return int(datetime.now().timestamp())


def get_datestr() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def dump_reddit_post(datestr, submission):
    url = submission.url.split('?')[0]
    if url.endswith('/'):
        url = url[:-1]

    def _save(fn):
        with open(os.path.join(DUMP_DIR_PATH, fn), 'w', encoding='utf-8') as fw:
            fw.write(submission.url + "\n\n")
            fw.write(submission.title + "\n\n")
            fw.write(submission.selftext)

    try:
        id_with_title = '_'.join(url.split('/')[-2:])
        fn = f"{datestr}_{id_with_title}.txt"
        _save(fn)
    except Exception:
        logger.warning(f"Fail to use fn={fn} with URL={url}")
        fn = f"{datestr}_{submission.id}.txt"
        logger.warning(f"Using fn={fn} instead...")
        _save(fn)


def load_rpp_cache() -> Dict[str, float]:
    """ Load Reddit pulled post cache"""
    cache_dict = {} # Key as URL, value as pulling stamp
    if os.path.isfile(CACHE_PKL_NAME):
        try:
            with open(CACHE_PKL_NAME, 'rb') as fo:
                cache_dict = pickle.load(fo)
        except:
            logger.warning(f"Fail to load back {CACHE_PKL_NAME}!")
            os.remove(CACHE_PKL_NAME)
            return {}

    return cache_dict


def save_rpp_cache(cache_dict:Dict[str,float]):
    """ Save Reddit pulled post cache"""
    with open(CACHE_PKL_NAME, 'wb') as fw:
        pickle.dump(cache_dict, fw)


if __name__ == '__main__':
    ### Start the Reddit dump process
    rppc_cache = load_rpp_cache()

    if not os.path.isdir(DUMP_DIR_PATH):
        os.makedirs(DUMP_DIR_PATH)

    st = datetime.now()
    datestr = get_datestr()
    logger.info(f"Start Reddit dumping at {datestr}...")
    time.sleep(1)

    # Obtain Submission Instances from a sub-reddit
    new_post_count = 0
    with tqdm(total=PULL_SIZE_LIMIT) as pbar:
        pc = 0
        for submission in st_googlepixel.new(limit=PULL_SIZE_LIMIT):
            if submission.url not in rppc_cache:
                rppc_cache[submission.url] = get_ts()
                dump_reddit_post(datestr, submission)
                new_post_count += 1

            pbar.update(1)
            pc += 1

        pbar.update(PULL_SIZE_LIMIT - pc)

    logger.info(f"Total {new_post_count:,d} new post collected! ({datetime.now() - st})")
    save_rpp_cache(rppc_cache)
