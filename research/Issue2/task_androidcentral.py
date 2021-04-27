#!/usr/bin/env python
import sys
from utils import *
from datetime import datetime


def start():
    ew = ExplorerWorker(
        name="androidcentral",
        src_url="https://www.androidcentral.com/",
        url_ptn=r'https?://www\.androidcentral\.com/[^/]+$',
        #test_run=10
    )
    st = datetime.now()
    print(f"Start working at {st.strftime('%Y-%m-%d/%H:%M:%S')}!")    
    ew.start()        
    ew.join()
    et = datetime.now()
    print(f"Done! ({et.strftime('%Y-%m-%d/%H:%M:%S')}/{et-st})")
    sys.exit(0)
    
  
if __name__ == '__main__':
    start()

