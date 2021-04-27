#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

r'''
Simple Inspection (sins): inspect sub folders ('blekko', 'html', 'old_te', 'new_te') by random sampling,
and generate sins_list.txt, where inspector can take notes.
Will invote fileMerge.app on MacOs as comparison tools for 'new_te' vs 'blekko', 'new_te' vs 'old_te'.
Will open browser for corresponding html files in 'html' folder.
'''

import os
import random
from sys import argv
from sys import platform
from datetime import datetime

gfn = {}  # file name
gfd = {}  # folder
gfn['idlist'] = 'sins_%s.txt' % datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
gfd['output'] = 'cms_scan'
subs = ['blekko', 'html', 'old_te', 'new_te']
suspicious_text = [
    'Similar Article',
    'Related Article',
    'Related News',
    'Related Reading'
]


def prepdir(output):
    global gfd, gfn
    gfd['output'] = output
    for sub in subs:
        gfd[sub] = os.path.join(gfd['output'], 'cmp', sub)
    return gfd, gfn


def compf(dir0, dir1, dir2, fn):
    ohtml = os.path.join(gfd['html'], fn)
    nhtml = os.path.join(gfd['html'], '%s.html' % fn)
    if os.path.exists(ohtml):
        with open(ohtml) as fin:
            with open(nhtml, 'w+') as fout:
                fout.write(fin.read())
        os.system('open %s' % nhtml)
    blekko = os.path.join(dir0, fn)
    oldte = os.path.join(dir1, fn)
    newte = os.path.join(dir2, fn)
    if all(os.path.exists(p) for p in [blekko, oldte, newte]):  # 3-way comparison
        print('Comparing %s/%s with %s/%s ...' % (dir0, fn, dir2, fn))
        os.system(  # compare new with blekko
            '/Applications/Xcode.app/Contents/Applications/FileMerge.app/Contents/MacOS/FileMerge -left "%s/%s" -right "%s/%s"' %
            (dir0, fn, dir2, fn)
        )
        print('Comparing %s/%s with %s/%s ...' % (dir1, fn, dir2, fn))
        os.system(  # compare new with readability
            '/Applications/Xcode.app/Contents/Applications/FileMerge.app/Contents/MacOS/FileMerge -left "%s/%s" -right "%s/%s"' %
            (dir1, fn, dir2, fn)
        )
    elif all(os.path.exists(p) for p in [oldte, newte]):  # 2-way comparison
        print('Comparing %s/%s with %s/%s ...' % (dir1, fn, dir2, fn))
        os.system(  # compare new with old
            '/Applications/Xcode.app/Contents/Applications/FileMerge.app/Contents/MacOS/FileMerge -left "%s/%s" -right "%s/%s"' %
            (dir1, fn, dir2, fn)
        )
    os.system('grep %s tools/cms_scan/idurls_fixed.csv' % fn)


def comp(dir0, dir1, dir2, num):
    def log(s):
        with open(gfn['idlist'], 'a+') as f:
            f.write(s)
            f.flush()

    fnlist = os.listdir(dir1)
    log('*** %s vs %s ***\n' % (dir1, dir2))
    random.shuffle(fnlist)
    for i in range(num):
        fn = fnlist[i]
        log('%s: ' % fn)
        compf(dir0, dir1, dir2, fn)
        ans = input('\nComment? ')
        log('%s\n' % ans)
        ans = input('\nContinue? [Y/n]')
        if ans == 'n':
            break


if len(argv) == 1:
    print(
        '$1: folder to be scanned\n'
        '$2: (optional) file to be scanned')
else:
    if platform != 'darwin':
        print('This program only works on MacOS.')
        exit()
    if len(argv) > 1:
        prepdir(argv[1])
        if os.path.exists(gfn['idlist']):
            os.unlink(gfn['idlist'])
    if len(argv) > 2:
        compf(gfd['blekko'], gfd['old_te'], gfd['new_te'], argv[2])
    else:
        try:
            num = int(input('Review how many random docs? [default: 30] '))
        except:
            num = 30
        comp(gfd['blekko'], gfd['old_te'], gfd['new_te'], num)
        ans = input('Scan suspicious text in all docs? [y/n] ')
        if ans == 'y':
            inslist = []  # inspection list
            for fn in os.listdir(gfd['new_te']):
                with open(os.path.join(gfd['new_te'], fn)) as f:
                    for l in f:
                        if any(t in l for t in suspicious_text):
                            inslist.append(fn)
                            break
            icount = len(inslist)
            if icount > 0:
                ans = input('%d docs found suspicious, review 10? [y/n] ' % icount)
                if ans == 'y':
                    random.shuffle(inslist)
                    for fn in inslist[:10]:
                        compf(gfd['blekko'], gfd['old_te'], gfd['new_te'], fn)
            else:
                print('%d docs found suspicious, no inspection required.' % icount)
