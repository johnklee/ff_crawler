#!/usr/bin/env python3
import os
import re
from .extractor_base import Handler, Postproc
from readability.readability import Document
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
from .te_policy import HParser


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''


################################
# Function(s)
################################

def simple_fact(ext_title=False):
    handler = HTML2TextHandler()

    if ext_title:
        handler.pp_list.append(P4Title())

    return handler


################################
# Class Definition
################################
class HTML2TextHandler(Handler):
    def __init__(self):
        super(HTML2TextHandler, self).__init__()

    def extract_link_from_html(self, url, content, body):
        uo = urlparse(url)
        base_url = "{scheme}://{netloc}".format(scheme=uo.scheme, netloc=uo.netloc)
        all_links = set()
        bdy_links = set()
        try:
            soup = BeautifulSoup(content, "html.parser")
            for atag in soup.find_all('a'):
                link = atag.get('href', '').strip()
                # Quick filter to skip weird link such as <a href="javascript:;" ...>
                if link.startswith('javascript') or link.startswith('mailto:') or not link:
                    continue

                if link.startswith('/'):
                    link = "{}{}".format(base_url, link)
                elif not link.startswith('http'):
                    # Handle relative path
                    link = urljoin(url, link)

                link = link[:-1] if link.endswith('/') else link

                if atag.string and atag.string in body:
                    bdy_links.add(link)
                    self.logger.debug('* {}\t{}'.format(link, atag.string))
                else:
                    self.logger.debug('{}\t{}'.format(link, atag.string))

                all_links.add(link)
        except:
            self.logger.exception('Fail to extract link from URL={}!'.format(url))

        return (list(all_links), list(bdy_links))

    def handle(self, url, content):
        # Fix of issue27
        # content = re.sub('href="(.*?)"', '', content);
        doc = Document(content)
        try:
            hp = HParser(doc.summary())
            text = doc.title() + '\n' + hp.tag_list[0].rtext().replace('==+NL+==', '\n')
            text = '\n'.join(list(map(lambda l: l.strip(), text.split('\n'))))
            text = re.sub('\n{3,}', '\n\n', text).strip()
            return text
        except:
            self.logger.exception('Fail to parse the summary from readability!')
            raise


class P4Title(Postproc):
    r'''
    Post process to extract title of article
    '''
    def __init__(self, dft=''):
        r'''
        :param dft: Default value to return if <title> tag doesn't exist
        '''
        super(P4Title, self).__init__('title')
        self.dft = dft

    def __call__(self, url, content, text, handler):
        soup = BeautifulSoup(content, "html.parser")
        if soup.title:
            return str(soup.title.string) if soup.title.string else ''
        else:
            self.logger.warning('{} does not have <title> tag!'.format(url))
            return self.dft
