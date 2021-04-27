#!/usr/bin/python3
import sys
import importlib
import os
import inspect
from importlib import util as importlib_util
from .logb import getLogger
# from .pdf2text import simple_fact as pdf_sfact
from .html2text import simple_fact as html_sfact
from .plain2text import simple_fact as pln_sfact


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''


################################
# Class Definition
################################

class TEAgent:
    ERR_MSG_MTYPE_NOT_SUPPORT = 'Content type={mtype} is not supported yet!'
    ''' Error message for unsupported MIME'''

    DEFAULT_RST = {'title': '', 'text': '', 'te_suc': False}

    def __init__(self, ext_title=False, disable_policy=False, policy_path=None):
        r'''
        Constructor

        :param ext_title: True to extract title; False otherwise
        :param disable_policy: True to disable loading policy
        '''
        self.logger = getLogger(os.path.basename(__file__))
        self.handlers = {
                            'text/html': html_sfact(ext_title=ext_title),
                            # 'application/pdf': pdf_sfact(ext_title=ext_title),
                            'text/plain': pln_sfact(ext_title=ext_title)
                        }  # key as Media type; value as corresponding handler

        if not disable_policy:
            if policy_path is None:
                policy_path = os.path.join(os.path.abspath(MODU_PATH), 'policy')

        self.load_policy(policy_path)

    def load_policy(self, policy_path, namespace=None, target_policy_names=None):
        r'''
        Loading policy stored in a given folder

        :param policy_path: Path of folder to store policy file
        :param namespace: Namespace used to control the import path
        :param target_policy_names: If given, only the policy module name exist in here will be loaded.

        :return:
            Number of policy file being loaded
        '''
        if os.path.isdir(policy_path):
            pc = 0
            for pf in list(filter(lambda f: f.endswith('.py') and f.startswith('policy'), os.listdir(policy_path))):
                if target_policy_names and pf.split('.')[0] not in target_policy_names:
                    self.logger.warning('Ignore {}!'.format(pf))
                    continue

                self.logger.debug('Loading {}...'.format(pf))
                try:
                    module_name = 'purifier.policy{}.{}'.format('' if namespace is None else ".{}".format(namespace), pf.split('.')[0])
                    spec = importlib_util.spec_from_file_location(module_name, os.path.join(policy_path, pf))
                    module = importlib_util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    for po, pn in list(filter(lambda t: callable(t[0]) and not inspect.isclass(t[0]), list(map(lambda n: (getattr(module, n), n), dir(module))))):
                        if hasattr(po, 'url_ptn'):
                            self.logger.debug('\tRegister {}'.format(po.url_ptn))
                            po.module_name = module_name
                            po.policy_name = pn
                            self.handlers[po.mime].regr(po.url_ptn, po)

                    pc += 1
                except:
                    self.logger.exception('Fail to load policy from {}!'.format(pf))

            return pc
        else:
            self.logger.warn('Policy folder={} does not exist!'.format(policy_path))
            return -1

    def parse(self, mtype, url, content, do_ext_link=False):
        r'''
        Parse the given content to do text extraction

        :param mtype: Content type in string. e.g.: 'text/html'.
        :param url: The source URL
        :param content: The corresponding content.
        :param do_ext_link: True to extract URL link from content (default:False)

        :return
            tuple(is_success, extraction result, reason)
        '''
        try:
            mtype = mtype.split(';')[0].strip()
            handler = self.handlers.get(mtype, None)
            if handler:
                try:
                    extract_rst = handler(url, content, do_ext_link)
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    return (False, TEAgent.DEFAULT_RST, {'reason': handler.reason(), 'err': "{}: {}".format(exc_type, exc_value)})

                if isinstance(extract_rst, dict) and 'title' not in extract_rst:
                    extract_rst['title'] = ''

                if (isinstance(extract_rst, dict) and extract_rst.get('te_suc', True)) or (isinstance(extract_rst, str) and extract_rst):
                    return (True, extract_rst, {'reason': handler.reason()})
                else:
                    return (False, extract_rst, {'reason': handler.reason(), 'err': 'Empty TE' if not handler.err_msg else handler.err_msg})
            else:
                self.logger.info("Use default agent...")
                return (False, TEAgent.DEFAULT_RST, {'reason': '?', 'err': TEAgent.ERR_MSG_MTYPE_NOT_SUPPORT.format(mtype=mtype, url=url)})
        except:
            self.logger.exception('Fail to parse content from URL={}!'.format(url))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            return (False, TEAgent.DEFAULT_RST, {'reason': '?', 'err': "{}: {}".format(exc_type, exc_value)})
