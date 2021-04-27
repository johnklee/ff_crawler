#!/usr/bin/python3
import os
import logging
from .extractor_base import Handler, Postproc
import base64
import tempfile
import pdfminer.settings
import pdfminer.high_level
import pdfminer.layout
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from io import StringIO


# Issue16 - Avoid multiple processes which cause conflict in writing same log file
os.environ['TIKA_LOG_PATH'] = os.getenv('TIKA_LOG_PATH', os.getcwd())   # noqa

from tika import tika
from tika import parser

pdfminer.settings.STRICT = False

################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''


################################
# Function(s)
################################
def simple_fact(ext_title=False):
    handler = PDFTika2TextHandler()

    if ext_title:
        handler.pp_list.append(P4Title())

    return handler


################################
# Class Definition
################################
class PDFTika2TextHandler(Handler):
    def __init__(self, tika_log_path=None, log_fname='tika.log'):
        super(PDFTika2TextHandler, self).__init__()
        if tika_log_path:
            log_file = os.path.join(tika_log_path, log_fname)
            tika.TikaServerLogFilePath = tika.log_path = tika_log_path
            # Remove all file handler
            tika.log.handlers = list(filter(lambda hdr: not isinstance(hdr, logging.FileHandler), tika.log.handlers))
            fileHandler = logging.FileHandler(log_file)
            fileHandler.setFormatter(tika.logFormatter)
            tika.log.addHandler(fileHandler)
            tika.log.info('Setup tika_log_path={}'.format(tika_log_path))

        parser.parse1 = tika.parse1
        parser.callServer = tika.callServer
        parser.ServerEndpoint = tika.ServerEndpoint
        self.tika = tika
        self.parser = parser

    def handle(self, url, content):
        r'''
        Tranform the input content into text format

        :param url: The source URL of given PDF content
        :param content: The PDF content (expected to be encoded with base64)

        :return: str object
        '''
        try:
            # For meet design in Blekko. Possibly change in the future.
            # Blekko will encode the content of PDF in base64
            bin_data_decode = base64.b64decode(content)
            self.parsed = self.parser.from_buffer(bin_data_decode)
            # print('parsed.metadata = {}'.format(self.parsed['metadata']))
            return self.parsed['content'].strip()
        except:
            self.logger.exception('Fail to handle content from URL={}'.format(url))

        return None


class PDFMiner2TextHandler(Handler):
    def __init__(self):
        super(PDFMiner2TextHandler, self).__init__()
        self.rsrcmgr = PDFResourceManager()

    def convert_pdf_to_txt(self, path, maxpages=0, caching=True, codec='utf8'):
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(self.rsrcmgr, retstr, codec=codec, laparams=laparams)
        with open(path, 'rb') as fp:
            interpreter = PDFPageInterpreter(self.rsrcmgr, device)
            pagenos = set()
            for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, caching=caching, check_extractable=True):
                interpreter.process_page(page)

        device.close()
        str = retstr.getvalue()
        retstr.close()
        return str

    def handle(self, url, content):
        r'''
        Tranform the input content into text format

        :param url: The source URL of given PDF content
        :param content: The PDF content (expected to be encoded with base64)

        :return: str object
        '''
        tmp_fn = None
        txt = None
        with tempfile.NamedTemporaryFile() as tmp:
            self.logger.debug('Write data into {}...'.format(tmp.name))
            bin_data_decode = base64.b64decode(content)
            tmp.write(bin_data_decode)
            tmp_fn = tmp.name
            txt = self.convert_pdf_to_txt(tmp.name)

        if tmp_fn and os.path.isfile(tmp_fn):
            self.logger.debug('Remove temple file as {}...'.format(tmp_fn))
            os.remove(tmp_fn)

        return txt


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
        if hasattr(handler, 'parsed') and 'pdf:docinfo:title' in handler.parsed['metadata']:
            return str(handler.parsed['metadata']['pdf:docinfo:title'])
        else:
            self.logger.warning('Fail to retrieve title from PDF from URL={}!'.format(url))
            return self.dft
