#!/usr/bin/env python
import sys
import os
import re
import string
import gensim.downloader as api
import pandas as pd
import numpy as np
import nltk
import pickle
from typing import Tuple
from tqdm import tqdm
from sklearn.cluster import MiniBatchKMeans, KMeans
from shutil import copyfile
from typing import Tuple


MONITOR_DIRS = [
    '/root/Issue2/androidcentral_pages_output',
    '/root/Issue2/androidpolicy_pages_output',
    '/root/Issue2/xdadev_pages_output',
]

INTERESTED_PAGE_DIR = '/root/Issue2/interested_pages'
STATS_DIR = '/root/Issue2/stats'
BT_CLUSTER_NUM = 147

wv = api.load('word2vec-google-news-300')
''' word to vector '''

kmeans_doc_cluster = pickle.load(open('kmeans_model.pkl', 'rb'))
''' KMeans cluster object '''


def read_content(fp):
    with open(fp, 'r') as fo:
        fo.readline() # Skip URL
        fo.readline()
        fo.readline() # Skip title
        fo.readline()
        return fo.read()


def doc2vec(content):
    doc_vec = np.zeros(300)
    for sent in nltk.sent_tokenize(content):
        for w in nltk.tokenize.word_tokenize(sent):
            try:
                doc_vec += wv[w]
            except:
                pass

    row = [content.count('\t')]
    row.extend(doc_vec.copy())
    return [row]


def search_pixel_kw(content:str) -> bool:
    return 'pixel' in content


def search_bt_kw(content:str, bt_kw={'bt', 'bluetooth'}) -> bool:
    words = set(content.split())
    new_words = []
    for w in words:
        if w and w[0] in string.punctuation:
            w = w[1:]

        if w and w[-1] in string.punctuation:
            w = w[:-1]

        if len(w) >= 2:
            new_words.append(w)

    if any(map(lambda w: w in bt_kw, new_words)):
        if kmeans_doc_cluster.predict(doc2vec(content))[0] == BT_CLUSTER_NUM:
            return True 

    return False


if __name__ == '__main__':
    print(f"Python execute path: {sys.executable}")
    stat_files = sorted(os.listdir(STATS_DIR))
    latest_stat_file = os.path.join(STATS_DIR, stat_files[-1]) if stat_files else None
    for mdir in MONITOR_DIRS:
        channel = os.path.basename(mdir)
        f_cnt = px_cnt = bt_cnt = 0
        f_cnt_diff = px_cnt_diff = bt_cnt_diff = 0
        for f in os.listdir(mdir):
            if f.endswith('.txt'):
                f_cnt += 1
                src_fp = os.path.join(mdir, f)
                content = read_content(src_fp).lower()
                if search_pixel_kw(content):
                    px_cnt += 1

                if search_bt_kw(content):
                    bt_cnt += 1
                    interested_page_fp = os.path.join(INTERESTED_PAGE_DIR, f)
                    if not os.path.isfile(interested_page_fp):
                        copyfile(src_fp, interested_page_fp)

        if latest_stat_file:
            with open(latest_stat_file, 'r') as fo:
                for line in fo:
                    mth = re.search(f"{channel}: f_cnt=([0-9,]+), px_cnt=([0-9,]+), bt_cnt=([0-9,]+)", line)
                    if mth:
                        f_cnt_diff = f_cnt - int(mth.group(1).replace(',', ''))
                        px_cnt_diff = px_cnt - int(mth.group(2).replace(',', ''))
                        bt_cnt_diff = bt_cnt - int(mth.group(3).replace(',', ''))

        if f_cnt_diff or px_cnt_diff or bt_cnt_diff:
            print(f"{channel}: f_cnt={f_cnt:,d} (+{f_cnt_diff}), px_cnt={px_cnt:,d} (+{px_cnt_diff}), bt_cnt={bt_cnt:,d} (+{bt_cnt_diff})")
        else:
            print(f"{channel}: f_cnt={f_cnt:,d}, px_cnt={px_cnt:,d}, bt_cnt={bt_cnt:,d}")

    print("")
