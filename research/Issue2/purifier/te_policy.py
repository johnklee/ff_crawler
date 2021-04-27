#!/usr/bin/python3
import os
import sys
import re
import html as html_modu
from html.parser import HTMLParser
from collections import OrderedDict
from .extractor_base import CTException
from .logb import getLogger

sys.path.insert(0, '.')
sys.setrecursionlimit(3000)


################################
# Constants
################################
MODU_PATH = os.path.dirname(__file__) if os.path.dirname(__file__) else './'
''' Path of current module '''


##################################
# Global Field
##################################
NEW_LINE_SIG = '==+NL+=='
''' New line placeholder '''


##################################
# Class Segment
##################################

class HTag:
    r'''
    Clz to hold HTML tag data. e.g.: div, html etc
    '''

    def __init__(self, tag, attrs):
        r'''
        :param tag:
            HTML tag name. e.g.: table/div
        :param attrs:
            List of attributes of current HTML tag. e.g.: [('id','id_val'), ('class', 'clz_val')]
        '''
        self.logger = getLogger(os.path.basename(__file__))
        self.tag = tag
        self.attrs = list(filter(lambda t: t[1] is not None, sorted(attrs, key=lambda t: t[0])))
        self.childs = []
        self.datas = []

    def __eq__(self, conditions):
        r'''
        This is implicitly to have similar functionality of function is_match when conditions is a tuple object.

        :param conditions:
            Condition to check equality. Different object has different behavior:
        '''
        if isinstance(conditions, tuple):
            try:
                return self.is_match(*conditions)
            except:
                self.logger.exception('Fail to do comparision with condition={}!'.format(conditions))
                return False
        elif isinstance(conditions, HTag):
            return self.tag == conditions.tag and self.attrs == conditions.attrs
        else:
            return False

    def insert(self, pos, tag_obj):
        r'''
        Insert child tag object at given position

        :param pos:
            Position to insert child tag object
        :param tag_obj:
            The child tag object
        '''
        self.childs.insert(pos, tag_obj)

    def add(self, tag_obj):
        r'''
        Add child tag object

        :param tag_obj:
            The child tag object
        :type tag_obj: `HTag` object
        '''
        self.childs.append(tag_obj)

    def is_match(self, tag_name, attr_name, attr_val, text_re=None):
        r'''
        Check if the given tag name/attribute name & value matching current tag object.

        :param tag_name:
            Name of HTML tag. e.g.: table
        :param attr_name:
            Name of attribute from HTML tag to search
        :param attr_val:
            Value of attribute to match
        :param text_re:
            regular expression to match text of tag
        '''
        if self.tag == tag_name or tag_name is None:
            is_hit = False
            # 1) Matching attribute
            if attr_name is None or attr_val is None:
                is_hit = True
            elif attr_name == 'text':
                text = self.rtext().replace(NEW_LINE_SIG, '\n').strip()
                if attr_val.startswith('r:'):
                    ptn = re.compile(attr_val[2:])
                    is_hit = True if ptn.match(text) else False
                else:
                    is_hit = (attr_val == text)
            elif attr_val.startswith('r:'):
                ptn = re.compile(attr_val[2:])
                is_hit = any(list(map(lambda t: t[0] == attr_name and ptn.match(t[1]), self.attrs)))
            else:
                is_hit = any(list(map(lambda t: t[0] == attr_name and t[1] == attr_val, self.attrs)))

            # 2) Matching content (text) if given
            if is_hit and text_re:
                return re.match(text_re, self.rtext()) is not None
            else:
                return is_hit

        return False

    def rtext(self, sep=None, ea=None, ia=None, er=False):
        r'''
        Translate datas into text recursively

        :param sep:
            Separator between data/text among different tag
        :param ea:
            Tuple(tag, attribute name, attribute value) to match ending tag
        :type ea: (tuple|list)
        :param ia:
            Tuple(tag, attribute name, attribute value) to match ignoring tag
        :type ia: (tuple|list)
        :param er:
            True to enable short quit which will stop collecting text right after
            satisfying ea.
        '''
        txt = ''
        csep = sep
        hit = False

        def _txt_pp(txt, stxt, tag):
            if tag == 'li':
                stxt.strip()
                stxt = stxt.replace('==+NL+==', '')
                if stxt.strip():
                    txt += '* ' + stxt + '\n'
            else:
                txt += stxt + csep

            return txt

        if self.tag in ['ul']:
            csep = sep = '\n'
        elif self.tag in ['div']:
            if self == ('div', 'class', r'r:crayon-line.*'):
                # Special fix for IOC in site unit42.paloaltonetworks.com
                csep = sep = ''
            else:
                csep = sep = ' '
        elif self.tag in ['a', 'p', 'article', 'strong', 'dd', 'dt', 'dl']:
            csep = sep = ''
        elif self.tag in ['td']:
            csep = sep = '\t'
        elif csep is None:
            if self.tag in ['p', 'input', 'span', 'time']:
                csep = sep = ''
            elif self.tag in ['td', 'tr']:
                csep = sep = '\t'
            elif self.tag in ['a', 'em']:
                csep = sep = ''
            elif self.tag in ['ul', 'li']:
                csep = sep = '\n'
            else:
                csep = '\n'
        elif self.tag not in ['tr', 'td']:
            if self.is_match('div', 'class', 'crayon-num') or \
               self.is_match('div', 'class', 'crayon-striped-num') or \
               self.is_match('div', 'class', 'crayon-nums-content'):
                csep = ' '
                sep = ' '
            elif self.is_match('div', 'class', 'crayon-line'):
                csep = ''
                sep = ''
            else:
                csep = sep = ''

        if self.tag == 'jtext':
            txt += csep.join(self.datas)
        elif self.tag in ['style', 'script']:
            txt = ''
        elif self.tag in ['br']:
            data_list = list(filter(lambda e: e != '\r\n', list(map(lambda e: e.replace(u'\xa0', u' ').replace(u'\r\n', ''), self.datas))))
            if data_list:
                if len(data_list) > 2 and data_list[0] == '\n' and data_list[1] == '\n':
                    data_list = data_list[1:]
                txt += ''.join(data_list)
        elif self.tag in ['form', 'script']:
            txt = ''
        else:
            for ct in self.childs:
                if ea is not None:
                    conditions = ea
                    if not isinstance(ea[0], tuple):
                        conditions = [ea]

                    if any(list(map(lambda sia: ct.is_match(*sia), conditions))):
                        hit = True
                        break

                if ia is not None:
                    if isinstance(ia, tuple):
                        if isinstance(ia[0], tuple):
                            test_cnds = list(map(lambda sia: ct.is_match(*sia), ia))
                            if any(test_cnds):
                                continue
                        elif ct.is_match(*ia):
                            continue

                if ea:
                    if er:
                        stxt, rhit = ct.rtext(sep, ea, er=er, ia=ia)
                        txt = _txt_pp(txt, stxt, ct.tag)
                        if rhit:
                            hit = True
                            break
                    else:
                        stxt = ct.rtext(sep, ea, ia=ia)
                        txt = _txt_pp(txt, stxt, ct.tag)
                else:
                    stxt = ct.rtext(sep, ia=ia)
                    txt = _txt_pp(txt, stxt, ct.tag)

        if er:
            return (txt, hit)
        else:
            return txt

    def rdata(self):
        r'''
        Retrieve text data recursively
        '''
        data_list = []
        if self.tag == 'jtext':
            data_list.extend(self.datas)
        else:
            for ct in self.childs:
                data_list.extend(ct.rdata())

        return data_list

    def text(self):
        r'''
        Retrieve text data recursively and combined them into str object.
        '''
        cdatas = [e.strip() for e in self.datas]
        cdatas = [e for e in cdatas if len(e) > 0]
        return '\n'.join(cdatas)

    def __str__(self):
        return str([self.tag, self.attrs, self.datas, self.childs])


class HParser(HTMLParser):
    r'''
    General purpose HTML Parser
    '''

    def __init__(self, html=None, ig_tags=[], dp_tags=[], ig_tags_with_data=[]):
        r'''
        Constructor

        :param html: HTML content to do parse
        :param ig_tags: Tag list to be ignored during parsing
        :param dp_tags: Tag list to be dropped during parsing
        :param ig_tags_with_data: Tag list to be ignored but keep the data of them
        '''
        HTMLParser.__init__(self)
        self.logger = getLogger(os.path.basename(__file__))
        ''' Logger object '''
        self.tag_dict = {}
        ''' Key as HTML tag; value as count of it'''
        self.ctag = None
        ''' Temporary attribute to hold HTML tag and corresponding attrs'''
        self._ctag_str = None
        ''' The current tag string '''
        self.tag_list = []
        ''' Exist HTML tag list in parsed document '''
        self.tagStack = []
        ''' Stack to hold tag(s) recursively '''
        self.ig_tags = ['colgroup', 'col', 'param', 'input', 'script', 'noscript', 'iframe', 'style', 'meta',
                        'link', 'embed', 'nav', 'form', 'button', 'head', 'input', 'textarea', 'label']
        ''' Tags to be ignored during process'''
        self.ig_tags_with_data = ['p', 'br', 'img', 'dt']
        ''' Tag(s) to be ingnored but keep the data inside it '''
        self.ig_no_data = ['dl']
        ''' Tag(s) to ignore insiding data '''
        self.tag_with_nl = ['dl', 'dd', 'h1', 'h2', 'h3', 'h4', 'h5', 'div', 'p', 'section', 'tr', 'header', 'blockquote']
        ''' Tag(s) with appending new line '''
        self.ig_with_nl = ['hr']
        ''' Tag(s) to ignore with new line'''
        self.tag_with_prefix_nl = ['ul', 'p', 'blockquote']
        ''' Tag(s) with new line as prefix'''
        self.dp_tags = []
        ''' Tag(s) to be dropped'''
        self.nestedP = False
        ''' Nested paragraph '''
        self.inside_dtag = None
        '''Flag to indicate the parsing status that inside a dropped tag'''

        if ig_tags:
            self.ig_tags = list(set(self.ig_tags) | set(ig_tags))

        if dp_tags:
            self.dp_tags = list(set(self.dp_tags) | set(dp_tags))

        if ig_tags_with_data:
            self.ig_tags_with_data = list(set(self.ig_tags_with_data) | set(ig_tags_with_data))

        if html:
            # self.feed(self.unescape(unicode(html, errors='ignore').encode('utf-8')))
            html = re.sub(r'<!--[\s\S]*?-->', '', html)
            html = re.sub(r'<!-\[if IE\]>[\s\S]*?<!\[endif\]->', '', html)
            html = re.sub(r'<!-\[if lte IE \d+\]>[\s\S]*?<!\[endif\]->', '', html)
            self.feed(html)

    def is_ignored_tag(self, tag, attrs=None):
        r'''
        Check if the given tag is in ignored tag list

        :param tag: Tag name to check if in ignored tag list
        :return: True if the given tag is in ignored tag list. False otherwise.
        '''
        for ig_tags in list(map(lambda an: getattr(self, an), filter(lambda an: an.startswith('ig_'), dir(self)))):
            if tag in ig_tags:
                return True

        return False

    def handle_starttag(self, tag, attrs):
        r'''
        Inherited API from HTMLParser

        @see:
            https://docs.python.org/2/library/htmlparser.html#HTMLParser.HTMLParser.handle_starttag
        '''
        if self.inside_dtag is not None:
            return

        ctag = HTag(tag.lower(), attrs)
        if ctag in self.dp_tags:
            self.inside_dtag = ctag
            self.logger.debug('Entering dropped tag: {}'.format(str(ctag)))
            return

        self.logger.debug('Handle starttag={}: {}'.format(tag, attrs))
        self.logger.debug('{}'.format('>'.join(list(map(lambda t: t.tag, self.tagStack)))))

        self._ctag_str = tag

        # New line as prefix
        if self.ctag and (tag in self.tag_with_prefix_nl or tag in self.ig_with_nl):
            txtTag = HTag('jtext', [])
            txtTag.datas.append('\n')
            self.ctag.add(txtTag)

        # Special handling for darkreading to avoid nested paragraph tag
        if tag == 'p' and len(self.tagStack) > 0 and self.tagStack[-1].tag == 'p':
            self.nestedP = True
            return

        # Special handling for unbalancing <li> tag. e.g.: cyberwatson-11535
        if tag == 'li' and self.ctag.tag == 'li':
            self.logger.debug('Pop out <li> tag for no nested li!')
            self.tagStack.pop()

        if ctag.tag == 'br':
            txtTag = HTag('jtext', [])
            txtTag.datas.append(NEW_LINE_SIG)
            if self.ctag:
                self.ctag.add(txtTag)
            return

        elif ctag.tag == 'p' and attrs:
            txtTag = HTag('jtext', attrs)
            txtTag.datas.append(NEW_LINE_SIG)
            ctag.insert(0, txtTag)
            return

        elif self.is_ignored_tag(ctag.tag, attrs):
            self.logger.debug('\tAs ignore tag: {}!'.format(ctag.tag))
            return

        self.tag_dict[tag] = self.tag_dict.get(tag, 0) + 1
        self.tag_list.append(ctag)
        if len(self.tagStack) > 0:
            self.tagStack[-1].add(ctag)     # Add child tags

        self.tagStack.append(ctag)
        self.ctag = ctag                    # Point to tag under process

    def handle_endtag(self, tag):
        r'''
        Inherited API from HTMLParser

        @see:
            https://docs.python.org/2/library/htmlparser.html#HTMLParser.HTMLParser.handle_endtag
        '''
        if self.inside_dtag and self.inside_dtag.tag == tag:
            self.logger.debug('Exiting dropped tag: {}'.format(str(self.inside_dtag)))
            self.inside_dtag = None
            return

        self.logger.debug('Handle endtag={}'.format(tag))

        if self.ctag and self.ctag.tag in self.tag_with_nl:
            txtTag = HTag('jtext', [])
            txtTag.datas.append(NEW_LINE_SIG)
            self.ctag.add(txtTag)

        # elif tag in self.ig_tags or \
        #     tag in self.ig_tags_with_data or \
        #     tag in self.ig_with_nl:
        if self.is_ignored_tag(tag):
            self._ctag_str = '?' if self.ctag is None else self.ctag.tag
            self.logger.debug('\tAs ignore tag: {}...ctag={}'.format(self.ig_tags, self._ctag_str))
            return

        # Depreciated code and should be removed in the future
        if tag == 'p' and len(self.tagStack) > 0 and self.tagStack[-1].tag != 'p':
            self.logger.debug('\tMultiple p issue with previous tag as {}!'.format(self.tagStack[-1].tag))
            return

        r'''
        if self.ctag.tag in self.ig_with_nl:
            txtTag = HTag('jtext', [])
            txtTag.datas.append(NEW_LINE_SIG)
            self.ctag.add(txtTag)
        '''

        # self.ctag = None
        if len(self.tagStack) > 0:
            if self.tagStack[-1].tag != tag:
                self.logger.debug('\tUnbalence tag={}!'.format(tag))
                if len(self.tagStack) > 1 and self.tagStack[-2].tag == tag:
                    self.logger.debug('\tRecover by remove tag={}!'.format(self.tagStack[-1]))
                    etag = self.tagStack.pop()
                else:
                    return

            self.ctag = None
            etag = self.tagStack.pop()
            # self.ctag = etag                # Point to tag under process
            # if self.ctag.tag == 'br':
            #    self.ctag.datas.append('\n')
            if len(self.tagStack) > 0:
                self.ctag = self.tagStack[-1]
                self._ctag_str = self.ctag.tag
                # logger.debug('\tctag={}'.format(self.ctag.tag))

            # logger.debug('{}'.format('>'.join(list(map(lambda t:t.tag, self.tagStack)))))
            return etag
        else:
            self.logger.debug('Empty tag stack...')

    def handle_data(self, data):
        r'''
        Inherited API from HTMLParser

        @see:
            https://docs.python.org/2/library/htmlparser.html#HTMLParser.HTMLParser.handle_data
        '''
        if self.inside_dtag is not None:
            return

        self.logger.debug('Handle data from {} ({:,d})'.format('?' if self.ctag is None else self.ctag.tag, len(data)))
        if self._ctag_str in self.ig_tags or self._ctag_str in self.ig_no_data and self._ctag_str not in ['br']:
            self.logger.debug('\tDiscard data for tag={}!'.format(self._ctag_str))
            return

        if self.ctag and self.ctag.tag in ['div', 'ul']:
            data = data.strip()

        if self.ctag and self.ctag.tag in ['li']:
            data = data.replace('\n', ' ')

        # data = data.strip() #  Comment out to solve issue946
        if self.ctag and self.ctag.tag in ['td', 'tr'] and data == '\n':
            # logger.debug('Discard data for td/tr with new line')
            return

        if len(self.tagStack) > 0 and len(data) > 0:
            self.tagStack[-1].datas.append(data)
            if self.nestedP:
                self.nestedP = False
                data = "\n{}".format(data)

            self.ctag.datas.append(data)
            textTag = HTag('jtext', [])
            textTag.datas.append(data)
            self.ctag.add(textTag)

    def qry_attr(self, tag, attr_name, attr_value):
        r'''
        Retrieve possible values of specific attribute (e.g. id/class)
        by given HTML tag (e.g. div/spam)

        :param tag:
            HTML tag to search
        :param attr_name:
            Name of attribute as search condition
        :param attr_value:
            Value of attribute as search condition

        :return:
            list of tag matching querying condition
        '''
        ttag_list = [t for t in self.tag_list if t.tag == tag]

        if attr_name is None or attr_value is None:
            return ttag_list
        else:
            return list(filter(lambda t: t.is_match(tag, attr_name, attr_value), ttag_list))

    def clean(self):
        r'''
        Reset parsing result
        '''
        self.ctag = None
        self.tag_list = []
        self.tag_dict = {}

    def read(self, fp):
        r'''
        Read content from given HTML file and parse it as well

        :param fp:
            HTML file path to be parsed
        '''
        with open(fp, 'r') as f:
            for line in f:
                try:
                    self.feed(self.unescape(line))
                except BaseException:
                    self.logger.error("Fail at line: {}".format(line))
                    raise


class HTCDummy:
    r'''
    Dummy Handler for default option
    '''

    def __init__(self):
        pass

    def handle(self, content, html):
        return (True, content)


class HTCExtractor:
    r'''
    HTML Content Text Extractor
    '''

    def __init__(self, eas, url_ptn, exp_url_ptn=None, mime='text/html', compact=False, ig_tags=[], dp_tags=[], ig_tags_with_data=[]):
        r'''
        Constructor

        :param eas:
            List of tuple(start tag matcher, end tag matcher, ignore tag matcher) as template (in parsing the HTML) which
            Start tag matcher'/'End tag matcher'/'Ignore tag matcher' is a tuple(tag name, attribute name, attribute value)
            - or -
            dict object with key as name of template; value as template
        :type eas: list/dict
        :param url_ptn:
            URL pattern to be registered for process scope
        :param exp_url_ptn:
            URL pattern to match excerpt page or unwanted page. Match will throw Exception here to stop CTE process.
        :param mime:
            Target MIME (Content-type)
        :param compact:
            True to compact the content by removing multiple new line.
        :param ig_tags:
            List of tag to be ignored during parsing
        :param dp_tags:
            List of tag to be dropped during parsing
        '''
        self.logger = getLogger(os.path.basename(__file__))
        self.eas_dict = OrderedDict() if isinstance(eas, OrderedDict) else {}
        if not isinstance(eas, dict):
            eas = {'default': eas}
        elif not isinstance(eas, OrderedDict):
            eas = OrderedDict(list(sorted(eas.items(), key=lambda t: t[0])))

        for k, v in eas.items():
            self.eas_dict[k] = list(map(lambda t: t if len(t) == 3 else (t[0], t[1], None), v))  # For backward compatibility

        self.policy_name = None
        self.module_name = None
        self.url_ptn = url_ptn
        self.exp_url_ptn = exp_url_ptn
        self.mime = mime
        self.compact = compact
        self.pek = None  # The 'e'as 'k'ey with success in parsing content from 'p'revious round
        self.ig_tags = ig_tags
        self.dp_tags = dp_tags
        self.ig_tags_with_data = ig_tags_with_data

    def __str__(self):
        if self.module_name:
            return "{} ({}/{}:{})".format(self.module_name, self.policy_name, self.pek, self.url_ptn)
        else:
            return "{} ({}/{}:{})".format(self.__module__, self.policy_name, self.pek, self.url_ptn)

    def reason(self):
        r'''
        Return tuple(module name, policy name, template name, matching logic)
        '''
        if self.module_name:
            return (self.module_name, self.policy_name, self.pek, self.url_ptn)
        else:
            return (self.__module__, self.policy_name, self.pek, self.url_ptn)

    def __repr__(self):
        return self.__str__()

    def _parse(self, hp, eas, url, sep='\n'):
        r'''
        Parsing the given HTML as `html` by given `eas`
        '''
        global NEW_LINE_SIG
        text = ''
        is_suc = True
        try:
            for ta, ea, ia in eas:
                optional = False
                if ta[0].startswith('?'):
                    optional = True
                    ta = (ta[0][1:], ta[1], ta[2])

                ttags = hp.qry_attr(*ta)

                if len(ttags) == 0:
                    self.logger.debug('Missing ta={}'.format(ta))
                    if optional:
                        continue

                    is_suc = False
                    break
                else:
                    for ttag in ttags:
                        stxt, rhit = ttag.rtext(ea=ea, ia=ia, er=True)
                        text += html_modu.unescape(stxt.strip()) + sep
                        if rhit:
                            self.logger.debug('Short quit at {}'.format(ttag))
                            break

            text = text.replace(NEW_LINE_SIG, '\n').strip()
            if self.compact:
                self.logger.debug('Compact the result...')
                text = '\n'.join(list(map(lambda l: l.strip(), text.split('\n'))))
                text = re.sub('\n{3,}', '\n\n', text)
                text = text.strip()

            return (is_suc, text)
        except Exception:
            self.logger.debug('Fail to handle given HTML with URL={}!'.format(url))
            return (False, None)

    def __call__(self, url, html, sep='\n'):
        r'''
        Apply customized text extraction on given HTML content.

        :param url:
            URL of given HTML.

        :param html:
            The HTML content to handle

        :param sep:
            Default separator for text extracted from desired tag(s) to join.

        :return:
            Tuple(Result of extracted text, True|False)
            If the second element of tuple is True, it means that extractor can handle the
            given HTML successfully. False otherwise.
        '''
        # Disable caching latest successful temporarily
        self.pek = None

        if isinstance(self.eas_dict, OrderedDict):
            self.pek = None  # for OrderedDict, always test by order, pek not used

        hp = HParser(html, ig_tags=self.ig_tags, dp_tags=self.dp_tags, ig_tags_with_data=self.ig_tags_with_data)
        if self.pek is not None:
            eas = self.eas_dict[self.pek]
            is_suc, text = self._parse(eas, url, sep)
            if is_suc:
                return text
            else:
                self.logger.debug('Fail in handler({})...'.format(self.pek))

        for k, eas in list(filter(lambda t: t[0] != self.pek, self.eas_dict.items())):
            self.logger.debug('Check handler={}...'.format(k))
            is_suc, text = self._parse(hp, eas, url, sep)
            if is_suc:
                self.pek = k
                return text
            else:
                self.logger.debug('Fail in handler({})...'.format(k))

        self.logger.debug('No available handler for URL={}'.format(url))
        raise CTException('No registered handler can process URL={}'.format(url))
