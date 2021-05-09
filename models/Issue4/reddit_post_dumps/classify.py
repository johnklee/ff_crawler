#!/usr/bin/env python
import os
import pickle
import re
import urllib.parse
import hashlib
import shutil
import logging
import numpy as np
import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from typing import List


FN_PTN = '\d{14}_[0-9a-zA-Z]{6,12}_.*\.txt'
''' File name pattern of dumped post. e.g.: 20210507070501_n6mhcu_airtag_competitor.txt '''

REDDIT_HOSTNAME = 'www.reddit.com'
''' Hostname of Reddit website '''

POS_DIR = "pos"
''' Directory to hold post as positive '''

NEG_DIR = 'neg'
''' Directory to hold post as negative '''

UKN_DIR = 'ukn'
''' Directory to hold post as unknown '''

DUP_DIR = 'dup'
''' Directory to hold post with duplicate content found '''

BT_KW_SET = {'bt', 'bluetooth'}
''' Keywords of Bluetooth '''

POST_CLASSIFIER_PKL_NAME = 'reddit_post_classifier.pkl'
''' File name of serialized reddit classifier model '''

VSET_SERIALIZED_FILENAME = 'reddit_vset.pkl'
''' verb set collected from model training as features '''

NEG_PROB_IGNORE_LOWER_BOUND = 0.95
''' Neg prob above this setting will be asked of permission to remove this post to neg folder '''


class color:
   LIGHTCORAL='\033[38;2;240;128;128m'
   LIGHTSKYBLUE='\033[38;2;135;206;250m'
   KHAKI='\033[38;2;240;230;140m'
   INDIGO='\033[38;2;72;0;130m'
   ORANGE='\033[38;2;255;165;0m'
   LIGHTRED='\033[1;31m'
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


def md5_val(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def get_fn_list() -> List[str]:
    fn_ptn = re.compile(FN_PTN)
    fn_list = []
    for f in os.listdir('.'):
        if fn_ptn.match(f):
            fn_list.append(f)

    return sorted(fn_list, reverse=True)


def show_help_msg():
    print("P: Label post as positive")
    print("N: Label post as negative")
    print("S: Skip")
    print("U: Label post as unknown")
    print("H: Show help message")
    print("Q: Quit")
    print("")


def read_post_from_file(fn):
    title = body = url = ''
    with open(fn, 'r', encoding='utf-8') as fo:
        url = fo.readline().strip()
        fo.readline()
        title = fo.readline().strip()
        fo.readline()
        body = fo.read().strip()

    return (title, body, url)


def text2words(text, min_len=2):
    word_set = set()
    for sent in sent_tokenize(text):
        for w in word_tokenize(sent):
            if len(w) < min_len:
                continue

            word_set.add(w.lower())

    return word_set


def display_fn_content(title, body, url):
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.netloc != REDDIT_HOSTNAME:
        print(color.BOLD + title + color.END)
        print(fn)
        print(color.BOLD + color.YELLOW + url + color.END + "\n\n")
        print(body + '\n\n')
        return False

    print(color.BOLD + title + color.END)
    print(fn)
    print(url + "\n\n")
    print(body + '\n\n')
    return True


def predict_proba(model, title, body, url, vset):
    '''
    Feature vector = [title_wv_300, body_wv_300, ohe_of_vset, num_of_bt, title_wset_size, body_wset_size]
    '''
    feats = []
    title_wset = set()
    body_wset = set()
    title_vec = np.zeros(300)
    body_vec = np.zeros(300)
    bt_count = 0
    for sent in nltk.sent_tokenize(body):
            for w in nltk.tokenize.word_tokenize(sent):
                w = w.lower()
                if w in BT_KW_SET:
                    bt_count += 1
                try:
                    body_vec += wv[w]
                    body_wset.add(wnl.lemmatize(w))                    
                except:
                    pass
                
    for w in nltk.tokenize.word_tokenize(title):
        w = w.lower()
        if w in BT_KW_SET:
            bt_count += 1
        try:
            title_vec += wv[w]
            title_wset.add(wnl.lemmatize(w))
        except:
            pass
        
    feats.extend(title_vec.copy())
    feats.extend(body_vec.copy())    
    for v in vset:
        if v in body_wset or v in title_wset:
            feats.append(1)            
        else:
            feats.append(0)
            
    feats.append(bt_count)
    feats.append(len(title_wset))
    feats.append(len(body_wset))
    return model.predict_proba([feats])[0]


if __name__ == '__main__':
    logging.info("Loading reddit post classifier into memory...")
    with open(os.path.join('..', POST_CLASSIFIER_PKL_NAME), 'rb') as fo:
        model = pickle.load(fo)

    with open(os.path.join('..', VSET_SERIALIZED_FILENAME), 'rb') as fo:
        vset = pickle.load(fo)

    fn_list = get_fn_list()
    is_done = False
    md5_set = set()
    logging.info(f"Collected {len(fn_list)} post file(s)...")
    for fn in fn_list:
        title, body, url = read_post_from_file(fn)
        neg_prob, pos_prob = predict_proba(model, title, body, url, vset)
        if neg_prob > NEG_PROB_IGNORE_LOWER_BOUND:
            print(f"Found negative post as {fn} (prob={neg_prob})!")
            display_fn_content(title, body, url)
            print("")
            ans = input(color.BOLD + color.RED + "Move to neg (y/s/u/q)? " + color.END).lower()
            if ans in ['y', 'yes']:
                shutil.move(fn, os.path.join(NEG_DIR, fn))
                continue
            elif ans in ['q', 'quit', 'exit']:
                break
            elif ans in ['u', 'unknown']:
                shutil.move(fn, os.path.join(UKN_DIR, fn))
                continue

        md5 = md5_val(title + '\n' + body)
        if md5 in md5_set:
            logging.warning(f"Duplicate content found: {fn}")
            shutil.move(fn, os.path.join(DUP_DIR, fn))
            continue

        md5_set.add(md5)
        word_set = text2words(title + '\n' + body)
        if not word_set.intersection(BT_KW_SET):
            logging.debug(f"Skip {fn}...")
            continue

        if display_fn_content(title, body, url):
            while True:
                choice = input(color.BOLD + color.BLUE + "Please enter (P/N/S/U/H/Q): " + color.END).lower()
                if choice == 'p':
                    # positive
                    shutil.move(fn, os.path.join(POS_DIR, fn)) 
                    break
                elif choice == 'n':
                    # negative
                    shutil.move(fn, os.path.join(NEG_DIR, fn))
                    break
                elif choice == 's':
                    # skip
                    break
                elif choice == 'u':
                    # unknown
                    shutil.move(fn, os.path.join(UKN_DIR, fn))
                    break
                elif choice == 'h':
                    # help
                    show_help_msg()
                elif choice == 'q':
                    # quit
                    is_done = True
                    break
                else:
                    display_fn_content(title, body, url)

        else:
            shutil.move(fn, os.path.join(UKN_DIR, fn))

        if is_done:
            break
