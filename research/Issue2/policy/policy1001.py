import os
import sys
from collections import OrderedDict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))   # noqa
from purifier.te_policy import HTCExtractor


policy_androidcentral_1 = HTCExtractor(
    [
        #(
        #    ('time', 'class', 'article-header__time'), None
        #),
        (('time', 'class', 'article-header__time'), None),
        (('div', 'class', 'r:article-body_.*'), ('div', 'class', 'bullet__body'))        
    ],
    url_ptn=r'r:https?://www\.androidcentral\.com/[^/]+$',
    compact=True,
)


policy_androidpolicy_1 = HTCExtractor(
    [
        (('h2', 'itemprop', 'name'), None),
        #(('time', 'class', 'timeago'), None),
        (('div', 'class', 'post-content'), None)
    ],
    url_ptn=r'r:https?://www\.androidpolice\.com/\d{4}/\d{1,2}/\d{1,2}/[^/]+/?$',
    compact=True,
)

policy_xdadep_1 = HTCExtractor(
    [
        (('div', 'class', 'entry_content'), ('h6', None, None))
    ],
    url_ptn=r'r:https?://www\.xda-developers\.com/[^/]+/?$',
    compact=True,
)
