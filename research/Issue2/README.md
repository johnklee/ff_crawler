## Introduction
For [Issue2](https://github.com/johnklee/ff_crawler/issues/2), we want to crawl websites to see if they contains the information we want. 
In order to achieve this task, we develop three scripts below to do so:
* `task_androidcentral.py`: Script used to crawl website `https://www.androidcentral.com/` (Category Rank 109)
* `task_androidpolicy.py`: Script used to crawl website `https://www.androidpolice.com/` (Category Rank 198)
* `task_xdadev.py`: Script used to crawl website `https://www.xda-developers.com/` (Category Rank 107)

##HowTo
To trigger the crawler task, just execute the corresponding script. For example:
```console
$ python task_xdadev.py
Start working at 2021-05-03/14:13:57!
...
```
The crawler will save the raw HTML page into `xdadev_cache` and the text extraction result into folder `xdadev_pages_output` from above case.
