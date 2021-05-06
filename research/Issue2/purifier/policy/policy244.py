#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))   # noqa
from purifier.te_policy import HTCExtractor


policy_itknowledgeexchange01_1 = HTCExtractor({
    'T1': [(
            ('div', 'class', 'post'),
            (
                ('span', 'class', 'postmetadata'),
                ('div', 'id', 'commentObject')
            ),
            (
                ('div', 'id', 'articleToolbar'),
                ('small', 'class', 'upper'),
                ('ul', 'id', 'social-icons-desktop'),
                ('div', 'class', 'tagContainer'),
                ('span', 'class', 'tagTitle'),
                ('div', 'class', r'r:podPress_content.*')
            )
    )]},
    url_ptn=r'r:https?://itknowledgeexchange\.techtarget\.com/[-_+%a-zA-Z0-9]+/[-_+%a-zA-Z0-9]+/?',
    exp_url_ptn=r'r:https?://itknowledgeexchange\.techtarget\.com/.*/\?page=\d+|'
                r'https?://itknowledgeexchange\.techtarget\.com/.*/tag/|'
                r'https?://itknowledgeexchange\.techtarget\.com/.*/page/\d+|'
                r'https?://itknowledgeexchange\.techtarget\.com/security-bytes/\d{4}/\d{2}/?',
    compact=True
)

policy_sans02_1 = HTCExtractor({
    'T1': [(
            ('div', 'class', 'content'),
            (
                ('div', 'class', 'sidebarBlurb ')
            ),
            (
                ('div', 'id', 'pre_footer')
            )
    )]},
    url_ptn=r'r:https?://www\.sans\.org/newsletters/at-risk/[a-z]+/\d+',
    exp_url_ptn=r'r:https?://www\.sans\.org/newsletters/at-risk/$',
    compact=True
)

policy_zscaler04_1 = HTCExtractor({
    'T1': [(
            ('section', 'id', 'post'),
            None,
            (
                ('li', 'class', 'rrssb-feed')
            )
    )],
    'T2': [(
            ('div', 'class', 'wrapper'),
            None,
            (
                ('li', 'class', 'rrssb-feed')
            )
    )]},
    url_ptn=(
        r'r:https?://www\.zscaler\.com/blogs/(research|corporate)/[a-z]+|'
        r'https?://www\.zscaler\.com/(security-advisories|security-research)/.+'),
    exp_url_ptn=r'r:https?://www\.zscaler\.com/blogs/(research|corporate)$',
    compact=True
)

policy_malwarebytesblog03_1 = HTCExtractor({
    'T1': [(
            ('div', 'id', 'content'),
            (
                ('div', 'class', 'share-section')
            ),
            (
                ('div', 'class', 'comments-section')
            )
    )]},
    url_ptn=r'r:https?://blog\.malwarebytes\.com/.*/\d{4}/\d{2}/[-_+%A-Za-z0-9]+/?',
    exp_url_ptn=r'r:https?://blog\.malwarebytes\.com/category/|https?://blog\.malwarebytes\.com/author/',
    compact=True,
    dp_tags=[('p', 'class', 'small'), ('p', 'class', 'breadcrumbs hidden-xs')]
)
