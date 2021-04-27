#!/usr/bin/env python
import sys
import os
import string

MONITOR_DIRS = [
    '/root/Issue2/androidcentral_pages_output',
    '/root/Issue2/androidpolicy_pages_output',
    '/root/Issue2/xdadev_pages_output',
]


def read_content(fp):
    with open(fp, 'r') as fo:
        fo.readline() # Skip URL
        fo.readline()
        fo.readline() # Skip title
        fo.readline()
        return fo.read()


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

    return any(map(lambda w: w in bt_kw, new_words))


if __name__ == '__main__':
    print(f"Python execute path: {sys.executable}")
    for mdir in MONITOR_DIRS:
        f_cnt = px_cnt = bt_cnt = 0
        for f in os.listdir(mdir):
            if f.endswith('.txt'):
                f_cnt += 1
                content = read_content(os.path.join(mdir, f)).lower()
                if search_pixel_kw(content):
                    px_cnt += 1
                    if search_bt_kw(content):
                        bt_cnt += 1

        print(f"{os.path.basename(mdir)}: f_cnt={f_cnt:,d}, px_cnt={px_cnt:,d}, bt_cnt={bt_cnt:,d}")

    print("")
