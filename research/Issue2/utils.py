import requests as reqlib
import os
import re
import random
import time
import pickle
import abc
import hashlib
import threading
from urllib.parse import urlparse
from purifier import TEAgent
from purifier.logb import getLogger
from enum import IntEnum
from typing import Tuple, List, Dict, Optional


class ScraperTimeout(Exception):
    def __init__(self, ex):
        self.ex = ex

    def __str__(self):
        return f"Timeout: {self.ex}"
        

class ScraperNot200(Exception):
    def __init__(self, sc):
        self.sc = sc
        
    def __str__(self):
        return f"Unexpected Status Code={self.sc}!"

class UnsupportedMIME(Exception):
    def __init__(self, mime):
        self.mime = mime
        
    def __str__(self):
        return f"Unsupported MIME={self.mime}!"
    

class Scraper(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, url):
        pass

class ReqScraper(object):
    def __init__(self, 
                 page_cache_path="page_caches",
                 headers={'User-Agent': 'Mozilla/5.0'},
                 skip_cache=False,
                 supported_mime_set={"text/html"}):
        self.page_cache_path = page_cache_path        
        if not os.path.isdir(self.page_cache_path):
            os.makedirs(self.page_cache_path)
            
        self.headers = headers            
        self.logger = getLogger(os.path.basename(self.__class__.__name__))
        self.skip_cache = skip_cache
        self.supported_mime_set = supported_mime_set
    
    def _get_cache_path(self, url):
        test_url_host = urlparse(url).netloc
        url_md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
        cache_file_name = f"{test_url_host}_{url_md5}.txt"
        cache_file_path = os.path.join(self.page_cache_path, cache_file_name)
        return cache_file_path

    def _del_from_cache(self, url):
        cache_file_path = self._get_cache_path(url)
        if os.path.isfile(cache_file_path):
            self.logger.warning("Removing cache file={cache_file_path}...")
            os.remove(cache_file_path)
    
    def _get_from_cache(self, url):
        cache_file_path = self._get_cache_path(url)        
        if os.path.isfile(cache_file_path):
            self.logger.debug(f"Return content of {url} from cache...")
            with open(cache_file_path, 'r', encoding='utf8') as fo:
                return fo.read()
            
        return None
    
    def _save2cache(self, url, html_content):
        cache_file_path = self._get_cache_path(url)
        with open(cache_file_path, 'w', encoding='utf8') as fw:
            fw.write(html_content)
    
    def get(self, url):
        if not self.skip_cache:
            cache_text = self._get_from_cache(url)
            if cache_text is not None:
                return cache_text
            
        self.logger.debug(f"Crawling {url}...")
        try:
            resp = reqlib.get(url, headers=self.headers, timeout=(5, 10))
            if resp.ok:
                mime = resp.headers['content-type'].split(';')[0].strip()
                self.logger.debug(f"URL={url} with MIME={mime}...")
                if mime.lower() not in self.supported_mime_set:
                    raise UnsupportedMIME(mime)
                
                self._save2cache(url, resp.text)
                return resp.text
            else:
                raise ScraperNot200(resp.status_code)
        except Exception as e:
            raise ScraperTimeout(e)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ThreadState(IntEnum):
    STOPPED = 0
    RUNNING = 1
    STOPPING = 2
    
    
class CrawlAgent(object):
    def __init__(self, name, throttling_range=(1, 2)):
        self.rs = ReqScraper(page_cache_path=f"{name}_cache")
        self.et = TEAgent(
            policy_path="policy", 
            disable_policy=True,
            ext_title=True
        )
        self.logger = getLogger(os.path.basename(self.__class__.__name__))
        self.throttling_range = throttling_range

    def obsolete_cache(self, url):
        self.rs._del_from_cache(url)
        
    def handle(self, url:str, skip_throttling:bool=False) -> Tuple[str, str, List[str]]:
        try:
            if skip_throttling:
                wait_in_sec = random.uniform(*self.throttling_range)
                self.logger.debug(f"throttling wait {wait_in_sec}s...")
                time.sleep(wait_in_sec)
                
            url_content_html = self.rs.get(url)
            is_succ, rst, handler = self.et.parse(
                "text/html", 
                url, 
                url_content_html,
                do_ext_link=True
            )
            if is_succ:
                return (rst['title'], rst['text'], rst['all_links'])
            else:
                return (rst['title'], rst['text'], rst['all_links'])
        except ScraperNot200 as e:
            self.logger.warning(f"Fail to handle URL={url}: {str(e)}")
            return None, None, None
        except UnsupportedMIME as e:
            self.logger.warning(f"Fail to handle URL={url}: {str(e)}")
            return None, None, None
        except ScraperTimeout as e:
            time.sleep(2)
            self.logger.warning(f"Fail to handle URL={url}: {str(e)}")
            return None, None, None

        
class ExplorerWorker(threading.Thread):
    def __init__(
        self, 
        name:str, 
        url_ptn:str, 
        src_url:str, 
        test_run:int=-1,
        page_saved_dir:Optional[str]=None):
        super(ExplorerWorker,  self ).__init__(name = name)
        self.name = name
        self.url_ptn = url_ptn
        self.src_url = src_url
        self.test_run = test_run
        self.ca = CrawlAgent(name)
        self.pc_dict = self._get_pc_dict()
        ''' Processed result cache: Key as URL; value as bool (True means this URL is crawled successfully)'''
        self.state = ThreadState.STOPPED
        ''' Thread state: 0-> stopped; 1-> running; 2-> stopping'''
        self.logger = getLogger(os.path.basename(self.__class__.__name__))
        ''' Logger object '''
        self.page_saved_dir = page_saved_dir if page_saved_dir is not None else f"{self.name}_pages_output"
        ''' Path or directory to save dump page'''
        self.stop_signal = f"STOP_{self.name}"
        ''' Stop signal file '''
        
        if not os.path.isdir(self.page_saved_dir):
            os.makedirs(self.page_saved_dir)
        
    def _get_output_page_path(self, url):
        url_host = urlparse(url).netloc
        url_md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
        page_file_name = f"{url_host}_{url_md5}.txt"
        page_file_path = os.path.join(self.page_saved_dir, page_file_name)
        return page_file_path
    
    def _get_pc_serialized_file(self) -> str:
        return f"{self.name}_pc_dict.pkl"
    
    def _get_pc_dict(self) -> Dict[str, bool]:
        pkl_file = self._get_pc_serialized_file()
        if os.path.isfile(pkl_file):
            with open(pkl_file, 'rb') as fo:
                return pickle.load(fo)
        else:
            return {}
    
    def _serialized(self):
        pkl_file = self._get_pc_serialized_file()
        with open(pkl_file, 'wb') as fo:
            pickle.dump(self.pc_dict, fo)
            
    def run(self):
        self.state = ThreadState.RUNNING
        url_queue = [self.src_url]
        pc = sc = fc = oc = 0
        while self.state == ThreadState.RUNNING and url_queue:
            if os.path.isfile(self.stop_signal):
                os.remove(self.stop_signal)
                self.logger.warning("Receive STOP signal!")
                break
            
            url = url_queue.pop(0)
            pc += 1
            if url not in self.pc_dict:
                # New URL
                self.logger.debug(f"Handling URL={url}...")
                title, content, collected_urls = self.ca.handle(url)
                if content is None:
                    self.pc_dict[url] = False
                    fc += 1
                else:
                    if url != self.src_url:
                        self.pc_dict[url] = True
                        
                    sc += 1
                    self.logger.info(bcolors.BOLD + f"Completed URL={url} ({len(url_queue):,d}/{pc:,d})"  + bcolors.ENDC)
                    next_level_urls = list(filter(lambda u: re.match(self.url_ptn, u) is not None and "#" not in u, collected_urls))
                    if next_level_urls:
                        self.logger.debug(f"\tCollected {len(next_level_urls)} next level URL(s)")
                        url_queue.extend(list(set(next_level_urls) - set(url_queue)))
                    
                    if content and "?" not in url:
                        page_output_path = self._get_output_page_path(url)
                        with open(page_output_path, 'w', encoding='utf8') as fw:
                            fw.write(f"{url}\n\n")
                            fw.write(f"{title}\n\n")
                            fw.write(f"{content}")
                            self.logger.debug(f"\tSaved page to {page_output_path}!")
            else:
                # Old URL
                if not self.pc_dict[url]:
                    self.logger.info(f"Skip broken URL={url} in the past...")
                    continue
                
                title, content, collected_urls = self.ca.handle(url, skip_throttling=True)
                if collected_urls:
                    next_level_urls = list(filter(lambda u: re.match(self.url_ptn, u) is not None, collected_urls))
                    url_queue.extend(list(set(next_level_urls) - set(url_queue)))
                    
                oc += 1
                self.logger.info(f"URL={url} is already handled...({len(url_queue):,d}/{pc:,d})")
                continue
                
            if self.test_run > 0:
                if (sc + fc) > self.test_run:
                    self.logger.info(f"Exceed test_run={self.test_run} and therefore stop running...")
                    break

            if pc % 1000 == 0:
                self.logger.info(bcolors.OKBLUE + bcolors.BOLD + f"{pc} URL completed: sc={sc:,d}; fc={fc:,d}; oc={oc:,d}\n" + bcolors.ENDC)
                self._serialized()
                self.ca.obsolete_cache(self.src_url)
                url_queue.append(self.src_url)
            
        self.logger.warning(f"Serialized explorer result (name={self.name})...")
        self._serialized()
        self.logger.warning(f"Explorer is stopped! (name={self.name})...")
        self.state = ThreadState.STOPPED
    
    def stop(self):
        self.logger.warning(f"Stopping explorer worker (name={self.name})...")
        if self.state == ThreadState.RUNNING:
            self.state = ThreadState.STOPPING
            while self.state != ThreadState.STOPPED:
                time.sleep(1)
        
