#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))   # noqa
from purifier.te_policy import HTCExtractor

policy_tenable01_1 = HTCExtractor(
    [
        (
            ('div', 'class', r'r:(app__content|content)'),
            (
                ('div', 'class', 'small mt2'),
                ('footer', None, None)
            ),
            (
                ('ul', 'class', 'socialcount socialcount-small no-bullet mb2'),
                ('div', 'class', 'back small')
            )
        ),
        (
            ('?aside', 'class', 'onethird last'), None
        )
    ],
    url_ptn=r'r:https?://www\.tenable\.com/(plugins|cve)/(nessus|nnm|lce|was|CVE-\d+-\d+)|'
            r'https?://www\.tenable\.com/(pvs|lce)-plugins/\d+|'
            r'https?://www\.tenable\.com/security/research/tra-\d{4}-\d{2}|'
            r'https?://www\.tenable\.com/webinars/[-_+%a-zA-Z0-9]+|'
            r'https?://www\.tenable\.com/security/tns-\d{4}-\d{2}',
    compact=True
)

policy_tenable01_2 = HTCExtractor(
    [
        (('header', 'class', 'blog-header'), None),
        (
            ('div', 'class', 'blog__container'),
            ('div', 'class', 'row blog-subscribe'),
            ('div', 'class', 'blog__sidebar-container')
        )
    ],
    url_ptn=r'r:https?://www\.tenable\.com/blog/(?!(technical$|executive/all$)).+',
    compact=True
)

policy_threatpost02 = HTCExtractor({
    'online': [
        (('header', 'class', 'c-article__header'), None),
        # (('div', 'class', 'c-article__meta-content'), None),
        (('div', 'class', 'c-article__main'), ('footer', 'class', 'c-article__footer'))
    ],
    'db': [
        (('header', 'class', 'entry-header'), None, ('div', 'class', 'post-info')),
        (('div', 'class', 'entry-content'), ('div', 'class', 'related-posts-inner'))
    ]},
    url_ptn=(
        r'r:https?://threatpost.com/[-_+%a-zA-Z0-9]+/\d+/?|'
        r'https?:\/\/threatpost\.com\/slide-shows\/.+'),
    # original
    # url_ptn=r'r:https?://threatpost.com/[-_+%a-zA-Z0-9]+/\d+/?',
    compact=True
)

policy_darkreading03_1 = HTCExtractor(
    [
        (('?h1', 'class', 'larger blue'), None),
        (('div', 'id', 'article-main'), ('span', 'class', 'smaller blue allcaps'))
    ],
    url_ptn=(
        r'r:https?:\/\/www\.darkreading\.com\/document\.asp|'
        r'https?://www\.darkreading\.com/(iot|threat-intelligence|risk|endpoint|vulnerabilities---threats|'
        r'careers-and-people|attacks-breaches|perimeter|operations|cloud|analytics)/.*/(d|a|v)/d-id/\d+'
    ),
    # # original
    # url_ptn=r'r:https?://www.darkreading.com/(iot|threat-intelligence|risk|endpoint|vulnerabilities---threats|'
    #         r'careers-and-people|attacks-breaches|perimeter|operations|cloud|analytics)/.*/(d|a)/d-id/\d+',
    compact=True
)

policy_darkreading03_2 = HTCExtractor(
    [
        (
            ('div', 'id', 'article-main'),
            (('div', 'id', 'more-insights'), ('span', 'class', 'smaller blue allcaps')),
            (('span', 'class', 'smaller blue allcaps'), ('div', 'style', r'r:background.*'))
        )
    ],
    url_ptn=r'r:https?://www\.darkreading\.com/.*/(a|d|v)/d-id/\d+|https?://www\.darkreading\.com/(a|d|v)/d-id/\d+',
    compact=True
)

policy_symantec04_1 = HTCExtractor(
    [
        (('div', 'class', 'text-content'), None),
        (('section', 'class', 'content-band'), None)
    ],
    url_ptn=(
        r'r:https?:\/\/www\.symantec\.com(\/[a-z]{2}\/[a-z]{2})?\/security-center\/vulnerabilities\/writeup\/\d+|'
        r'https?:\/\/www\.symantec\.com\/[a-z]{2}\/[a-z]{2}\/security-center\/writeup\/\d+'),
    # original
    # url_ptn=r'r:^https?://www.symantec.com/security-center/vulnerabilities/writeup/\d+$',
    compact=True
)

policy_symantec04_2 = HTCExtractor({
    'online': [
        (('div', 'class', 'main-content'), None, ('div', 'class', 'breadcrumbs-wrapper'))
    ],
    'db': [
        # (('div', 'class', r'r:contentPane.*'), ('div', 'class', 'colSide unitRight'), ('div', 'class', 'unitRight colTwoStyle21')) No copyright
        (('div', 'class', r'r:contentPane.*'),
         # (('div', 'class', 'r:colSide unitRight'), ('h3', None, None, 'References.*')), <--- Short stop while tag contain 'References' message
         (('div', 'class', 'r:colSide unitRight')),
         (('div', 'class', 'r:unit.*'),
          ('div', 'class', 'r:unitRight.*'),
          ('ul', 'class', 'clearfix tabsNav unit'),
          ('div', 'class', 'colSide unitRight'),
          ('div', 'class', 'hr2 mrgnTopMD'),
          ('div', 'class', 'breadcrumbs.*'),
          ('div', 'class', 'imgMrgnTopLG'))),
    ]},
    url_ptn=r'r:https?://www\.symantec\.com/security_response/writeup.jsp\?docid=.*|' \
            r'https?://www\.symantec\.com/[-_a-z]{2,5}/[-_a-z]{2,5}/security_response/writeup.jsp\?docid=.*|' \
            r'https?://www\.symantec\.com/security-center/writeup/\d{4}-\d+-\d+-\d+|' \
            r'https?://www\.symantec\.com/security_response/vulnerability.jsp\?bid=\d+',
    compact=True
)

policy_symantec04_3 = HTCExtractor({
    'db': [
        (
            ('div', 'id', 'content-content'),
            (
                ('div', 'class', 'terms clearfix'),
                ('div', 'id', 'comments')
            ),
            (
                ('div', 'class', 'node-posted'),
                ('div', 'class', 'node-meta clearfix'),
                ('div', 'class', 'clearfix'),
                ('div', 'class', 'filed-under item-article'),
                ('div', 'class', 'links-bar clearfix')
            )
        )
    ],
    'online': [
        (('h1', 'class', 'page-title ng-binding'), None),
        (
            ('div', 'class', 'article-body'),
            (
                ('ul', 'class', 'article-meta-footer'),
                ('ul', 'class', 'attachments ng-hide')
            )
        )
    ]},
    url_ptn=r'r:https?://www\.symantec\.com/connect/(articles|downloads|events)/[-_+=%a-zA-Z0-9]+(\?page=.*)?$',
    compact=True
)

policy_symantec04_4 = HTCExtractor({
    'db': [
        (
            ('div', 'class', 'contentPane'),
            None
        )
    ]},
    url_ptn=r'r:https?://www\.symantec\.com/security_response/earthlink_writeup.jsp\?docid=\d{4}-\d+-\d+-\d+',
    compact=True
)

policy_bankinfosecurity06_1 = HTCExtractor(
    [
        (
            ('article', 'id', 'generic-article'),
            (
                ('div', 'id', 'topicsBar'),
                ('div', 'class', 'row nav-articles')
            ),
            (
                ('div', 'class', 'r:share-this-buttons.*'),
                ('span', 'class', 'article-byline'),
                ('aside', 'id', 'sidebar'),
                ('article', 'class', 'r:excerpt.*')
            )
        )
    ],
    url_ptn=r'r:https?://www\.bankinfosecurity\.com/[-_+%0-9a-zA-Z]*-a-\d+(/op-\d+)?|'
            r'https?://www\.bankinfosecurity\.com/articles\.php\?art_id=\d+.*|'
            r'https?://www\.bankinfosecurity\.com/events/[-_+%0-9a-zA-Z]*-e-\d+(/op-\d+)?|'
            r'https?://www\.bankinfosecurity\.com/press-releases/[-_+%0-9a-zA-Z]*-p-\d+(/op-\d+)?|'
            r'https?://www\.bankinfosecurity\.com/agency-releases/[-_+%0-9a-zA-Z]*-r-\d+(/op-\d+)?',
    compact=True,
    dp_tags=[('p', 'class', 'text-muted')]
)

policy_bankinfosecurity06_2 = HTCExtractor(
    [
        (
            ('article', 'class', r'r:(asset blog-article.*|asset asset-img-res|asset webinar-intro|asset|asset single whitepaper)'),
            (
                ('div', 'id', 'topicsBar'),
                ('div', 'class', 'row nav-articles')
            ),
            (
                ('div', 'class', 'r:share-this-buttons.*'),
                ('span', 'class', 'article-byline'),
                ('aside', 'id', 'sidebar'),
                ('article', 'class', 'r:excerpt.*')
            )
        )
    ],
    url_ptn=r'r:https?://www\.bankinfosecurity\.com/blogs\.php\?postID=\d+|'
            r'https?://www\.bankinfosecurity\.com/blogs/[-_+%0-9a-zA-Z]*-p-\d+(/op-\d+)?|'
            r'https?://www\.bankinfosecurity\.com/interviews/[-_+%0-9a-zA-Z]*-i-\d+(/op-\d+)?|'
            r'https?://www\.bankinfosecurity\.com/webinars.php\?webinarID=\d+|'
            r'https?://www\.bankinfosecurity\.com/webinars/[-_+%0-9a-zA-Z]*-w-\d+(/op-\d+)?|'
            r'https?://www\.bankinfosecurity\.com/whitepapers/[-_+%0-9a-zA-Z]*-w-\d+(/op-\d+)?|'
            r'https?://www\.bankinfosecurity\.com/whitepapers\.php\?wp_id=\d+|'
            r'https?://www\.bankinfosecurity\.com/handbooks\.php\?hb_id=\d+|'
            r'https?://www\.bankinfosecurity\.com/interviews\.php\?interviewID=\d+|'
            r'https?://www\.bankinfosecurity\.com/podcasts\.php\?podcastID=\d+|'
            r'https?://www\.bankinfosecurity\.com/webinarsDetails\.php\?webinarID=\d+',
    compact=True,
    dp_tags=[('p', 'class', 'text-muted')]
)

policy_hackdig07 = HTCExtractor({
    't1': [
        (('div', 'id', 'topTitle'), None),
        (('h2', 'class', 'arttitle'), None),
        (
            ('div', 'id', 'content'),
            ('div', 'id', 'digit'),
            (
                ('div', 'style', r'r:display:none.*'),
                ('div', 'class', 'apart-alt tags')
            )
        )
    ],
    't2': [
        (('div', 'id', 'topTitle'), None),
        (('div', 'id', 'post'), ('div', 'id', 'digit')),
    ]},
    url_ptn=r'r:https?://en.hackdig.com/\d+/\d+.htm|https?://en.hackdig.com/\?\d+\.htm!?',
    compact=True,
    ig_tags_with_data=['span']
)

policy_seclists05_1 = HTCExtractor(
    [
        (('table', 'style', 'r:table-layout.*'), None, (('font', 'size', '+1'), ('form', 'id', 'r:top.*'), ('a', 'href', 'r:date.*'), ('a', 'href', 'r:index.*'), ('font', 'color', '#FFFFFF'), ('ul', 'style', 'r:margin.*')))
    ],
    url_ptn=r'r:^https?://seclists.org/bugtraq/\d{4}/[a-zA-Z]+/.*|https?://seclists.org/oss-sec/\d{4}/[a-zA-Z]+\d+/.*|https?://seclists.org/fulldisclosure/\d{4}/[a-zA-Z]+/.*',
    compact=True
)

policy_searchsecurity08_1 = HTCExtractor(
    [
        (('h1', 'class', 'main-article-title'), None),
        (('h2', 'class', 'main-article-subtitle'), None),
        (
            ('section', 'id', 'content-body'),
            (
                ('section', 'id', 'publish-date'),
                ('section', 'id', 'dig-deeper'),
                ('section', 'id', 'ask-an-expert')
            ),
            (
                ('div', 'id', 'inlineRegistrationWrapper'),
                ('div', 'class', 'sidebar alignRight'),
                ('div', 'class', r'r:ad-wrapper.*'),
                ('div', 'class', r'r:aside extraInfo.*')
            )
        )
    ],
    url_ptn=r'r:https?://searchsecurity.techtarget.com/(?!(blog/)).+',
    compact=True
)

policy_searchsecurity08_2 = HTCExtractor(
    [
        (('h1', 'class', 'main-article-title'), None),
        (('section', 'id', 'content-body'), None)
    ],
    url_ptn=r'r:https?://searchsecurity.techtarget.com/blog/Security-Bytes/.+',
    compact=True
)

policy_sans9_1 = HTCExtractor(
    [
        (('div', 'class', 'diary'),
         ('div', 'class', 'diarykeywords'),
         (('div', 'class', 'diaryheader'),
          ('a', 'class', 'ico-comments'),
          ('ul', 'class', 'ss-share')))
    ],
    url_ptn=r'r:https?://isc.sans.edu/diary/[-.+_%a-zA-Z0-9]+/\d+/?',
    compact=True
)

policy_sans9_2 = HTCExtractor(
    [
        (('table', 'class', 'postList'), ('td', 'class', 'user'), (('ul', 'class', 'ss-share')))
    ],
    url_ptn=r'r:https?://isc.sans.edu/forums/diary/[-.+_%a-zA-Z0-9]+/\d+/?',
    compact=True
)

policy_infosecurity10_1 = HTCExtractor(
    [
        (('h1', 'itemprop', 'name'), None),
        (('div', 'class', 'article-body'), None, (('div', 'class', 'sticky-share')))
    ],
    url_ptn=r'r:https?://www.infosecurity-magazine.com/news/[-_+%.a-zA-Z0-9]+/?|https?://www.infosecurity-magazine.com/blogs/[-_+%.a-zA-Z0-9]+/?',
    compact=True
)
