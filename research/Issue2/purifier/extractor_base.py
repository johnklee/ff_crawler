#!/usr/bin/env python3
import re
import os
from abc import ABC, abstractmethod
from .logb import getLogger


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''

ERR_MSG_HIT_EPP = 'Hit Excerpt Page URL pattern'
''' Message for hitting excerpt page URL pattern '''

ERR_MSG_BKN_PCY = 'Broken policy'
''' Message for broken policy '''


################################
# Class Definition
################################
class CTException(Exception):
    ''' Exception caused by customized text extraction '''
    pass


class EPException(Exception):
    ''' Exception caused by matching excerpt page URL pattern'''
    pass


class Postproc(ABC):
    def __init__(self, name):
        self.name = name
        self.logger = getLogger(os.path.basename(__file__))

    @abstractmethod
    def __call__(self, url, content, text, handler):
        pass


class Handler(ABC):
    PATTERN_URL = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    def __init__(self):
        self.logger = getLogger(os.path.basename(__file__))
        ''' Logger object '''
        self.stg_dict = {}
        ''' Strategy dict with key as URL pattern, value as policy'''
        self.p_stg = None
        ''' Placeholder to hold last applying stragety'''
        self.pp_list = []
        ''' Post processor list '''
        self.err_msg = None
        ''' Error message for reference '''

    def regr(self, url_ptn, stg):
        r'''
        Register strategy for handling text extraction on URL fit given pattern

        :param url_ptn: URL pattern. If the pattern starts with 'r:' which means the pattern is written in regular expression.
        :param stg: Strategy of text extraction
        :type stg: callable object
        '''
        self.stg_dict[url_ptn] = stg

    def _select_stg(self, url):
        r'''
        Select strategy based on given URL

        :param url: URL to select strategy
        :param rst_dict: dict object to update information

        :return: The registered handler for given URL
        '''
        self.p_stg = None
        self.err_msg = None
        for uptn, stg in self.stg_dict.items():
            if hasattr(stg, 'exp_url_ptn') and stg.exp_url_ptn is not None:
                if stg.exp_url_ptn.startswith('r:'):
                    if re.match(stg.exp_url_ptn[2:], url):
                        self.p_stg = stg
                elif stg.exp_url_ptn == url:
                    self.p_stg = stg

                if self.p_stg:
                    raise EPException('Hit exp_url_ptn: {}'.format(self.p_stg.exp_url_ptn))

            if uptn.startswith('r:'):
                if re.match(uptn[2:], url):
                    return stg
            elif uptn == url:
                return stg

        return self.handle

    def extract_link_from_html(self, url, content, text):
        r'''
        Only handler to process MIME type as text/html need to override this method

        :param url: URL of content
        :param content: Content for text extraction
        :param text: Text extraction result of content

        :return:
            Tuple(
                    all_links,      # list of link(s) collected from HTML,
                    body_a_links    #list of link(s) with text included by extracted text
                 )
        '''
        return ([], [])

    def reason(self):
        r'''
        Return the message of handler
        '''
        if self.p_stg:
            if hasattr(self.p_stg, 'reason'):
                return self.p_stg.reason()
            else:
                return (self.__class__.__name__ if self.p_stg.__class__.__name__ == 'method' else str(self.p_stg), None)
        else:
            return ('?', None)

    def extract_link_from_text(self, text):
        r'''
        Extract URL link from extracted text

        :param text: Extracted text from content

        :return:
            list object to hold collected link(s)
        '''
        links = re.findall(Handler.PATTERN_URL, text)
        links = list(set(list(map(lambda u: u[:-1] if u.endswith('/') else u, links))))
        return links

    def __call__(self, url, content, do_ext_link):
        r'''
        Launch text extraction logic

        :param url: URL of content
        :param content: Content to do text extraction
        :param do_ext_link: True to extract URL link from content

        :return:
            do_ext_link = True: Tuple(
                                        extracted_text,   # Extracted text
                                        all_links,        # All link(s) collected from tag <a>
                                        body_a_links,     # <a> tag with text included in extracted text
                                        body_txt_links    # Use re to extract URL from extracted text
                                     )
            do_ext_link = False: str object as extracted text.
        '''
        rst_dict = {}
        try:
            self.p_stg = self._select_stg(url)
            extracted_text = self.p_stg(url, content)
            rst_dict['te_suc'] = True
        except EPException:
            extracted_text = ''
            rst_dict['te_suc'] = False
            self.err_msg = ERR_MSG_HIT_EPP
        except CTException:
            extracted_text = ''
            rst_dict['te_suc'] = False
            self.err_msg = ERR_MSG_BKN_PCY
        except:
            extracted_text = ''
            self.logger.exception('Failed in text extraction step!')
            rst_dict['te_suc'] = False

        rst_dict['text'] = extracted_text

        if do_ext_link:
            all_links, body_a_links = self.extract_link_from_html(url, content, extracted_text)
            body_txt_links = self.extract_link_from_text(extracted_text)
            rst_dict['all_links'] = all_links
            rst_dict['body_a_links'] = body_a_links
            rst_dict['body_txt_links'] = body_txt_links

        for pp in self.pp_list:
            try:
                rst_dict[pp.name] = pp(url, content, extracted_text, self)
            except:
                self.logger.exception('Failed in post process as {}!'.format(pp.name))

        if len(rst_dict) == 1:
            return list(rst_dict.values())[0]
        else:
            return rst_dict

    @abstractmethod
    def handle(self, url, content):
        r'''
        Extract text content from given content

        :param url: URL of content
        :param content: Content to do text extraction
        '''
        pass


class EchoStrategy:
    r'''
    Testing Strategy which will echo the given string
    '''
    def __init__(self, et_rst='For testing'):
        self.et_rst = et_rst

    def __call__(self, url, content):
        return self.et_rst


class DummyPP(Postproc):
    r'''
    Dummy Post Processer which alwasy return empty string
    '''
    def __init__(self, name):
        r'''
        :param dft: Default value to return if <title> tag doesn't exist
        '''
        super(DummyPP, self).__init__(name)

    def __call__(self, url, content, text, handler):
        return ''
