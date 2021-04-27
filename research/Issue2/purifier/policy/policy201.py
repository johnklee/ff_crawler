#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# BEGIN LICENSE
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2019. All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
# END LICENSE

import os
import sys
from collections import OrderedDict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))   # noqa
from purifier.te_policy import HTCExtractor

policy_dshield01_1 = HTCExtractor({
    'forum': [
        (
            ('table', 'class', 'postList'),
            ('td', 'class', 'user'),
            None
        )
    ],
    'diary': [
        (
            ('div', 'class', 'diary'),
            ('div', 'class', 'diarykeywords'),
            (
                ('div', 'class', 'diaryheader'),
                ('a', 'class', 'ico-comments')
            )
        )
    ]},
    url_ptn=r'r:https?://.*dshield.org/(forums/|diary/|diary.html).+(\d/|\d|\d=)$',
    compact=True
)

policy_csoonline02_1 = HTCExtractor(OrderedDict({
    'article': [
        (
            ('h1', 'itemprop', 'headline'),
            None,
            None
        ),
        (
            ('?section', 'class', 'deck viewability'), None
        ),
        (
            ('div', 'itemprop', 'articleBody'),
            ('div', 'class', 'end-note'),
            (
                ('section', 'class', 'pagination'),
                ('div', 'class', 'connatix'),
                ('aside', 'class', r'r:fakesidebar.*')
            )
        )
    ],
    'amp-article': [
        (
            ('h1', 'class', 'art-title'),
            None,
            None
        ),
        (
            ('?section', 'class', 'deck viewability'), None
        ),
        (
            ('article', None, None),
            ('amp-embed', None, None),
            (
                ('div', 'class', 'ad-container'),
                ('div', 'class', 'dealpost-container'),
                ('aside', 'class', r'r:fakesidebar.*')
            )
        )
    ],
    'review-article': [
        (
            ('h1', 'itemprop', 'headline'),
            None,
            None
        ),
        (
            ('?section', 'class', 'deck viewability'), None
        ),
        (
            ('div', 'itemprop', 'reviewBody'),
            ('div', 'id', 'content-recommender'),
            (
                ('section', 'class', 'pagination'),
                ('aside', 'class', r'r:fakesidebar.*'),
                ('div', 'class', 'end-note'),
                ('div', 'class', r'r:.*tags'),
                ('div', 'class', 'article-intercept')
            )
        )
    ],
    'intro-slides': [
        (
            ('h1', 'itemprop', 'headline'),
            None,
            None
        ),
        (
            ('?section', 'class', 'deck viewability'), None
        ),
        (
            ('div', 'class', 'intro'),
            None,
            None
        )
    ],
    'online-slides': [
        (
            ('h1', 'itemprop', 'headline'),
            None,
            None
        ),
        (
            ('?section', 'class', 'deck viewability'), None
        ),
        (
            ('div', 'class', 'body-content small'),
            None,
            None
        )
    ],
    'db-slides': [
        (
            ('h1', 'itemprop', 'headline'),
            None,
            None
        ),
        (
            ('?section', 'class', 'deck viewability'), None
        ),
        (
            ('figcaption', None, None),
            None,
            (
                ('div', 'class', 'slideshow-bottom-nav')
            )
        )
    ]}),
    url_ptn=r'r:https?://www.csoonline.com/article/((?!google\.com/).)*$',
    compact=True
)

policy_mcafee03_1 = HTCExtractor(OrderedDict({
    'blog': [
        (
            ('div', 'class', 'container-fluid'),
            None,
            None
        ),
        (
            ('div', 'class', 'wrap-section padding-small article'),
            None,
            None
        )
    ],
    'blog_old': [
        (
            ('h1', 'class', 'entry-title'),
            None,
            None
        ),
        (
            ('div', 'class', 'entry-content'),
            ('footer', 'class', 'entry-footer'),
            None
        )
    ],
    'press': [
        (
            ('h1', 'id', 'dynamicTitleID'),
            None,
            None
        ),
        (
            ('div', 'id', 'press_release_container'),
            ('footer', None, None),
            None
        )
    ],
    'dynamic': [
        (
            ('h1', 'id', 'dynamicTitleID'),
            None,
            None
        ),
        (
            ('div', 'class', 'col-md-9 col-sm-12 padding-bottom-small'),
            ('div', 'class', 'col-md-3 col-sm-12 padding-bottom-medium'),
            None
        )
    ],
    'dashboard': [
        (
            ('h1', 'id', 'dynamicTitleID'),
            None,
            None
        ),
        (
            ('div', 'class', r'r:col-xs-12 grid-item .* text-left'),
            ('footer', None, None),
            (
                ('div', 'class', 'img-block')
            )
        )
    ],
    'dashboard-item': [
        (
            ('h1', 'id', 'dynamicTitleID'),
            None,
            None
        ),
        (
            ('div', 'class', r'r:container  large text-center wow fadeInUp.*'),
            ('footer', None, None),
            (
                ('ul', 'class', r'r:nav-tabs.*')
            )
        )
    ],
    'dashboard-list': [
        (
            ('h1', 'class', 'main-title'),
            None,
            None
        ),
        (
            ('div', 'class', 'row row-centered'),
            ('footer', None, None),
            (
                ('ul', 'class', r'r:nav-tabs.*')
            )
        )
    ],
    'threat-research': [
        (
            ('h1', 'id', 'dynamicTitleID'),
            None,
            None
        ),
        (
            ('div', 'class', 'container  large'),
            ('footer', None, None),
            None
        )
    ],
    'threat-research-old': [
        (
            ('h1', 'id', 'dynamicTitleID'),
            None,
            None
        ),
        (
            ('div', 'class', 'container  medium'),
            ('footer', None, None),
            (
                ('a', 'href', r'r:mailto:')
            )
        )
    ],
    'threat-intelligence': [
        (
            ('h1', None, None),
            None,
            None
        ),
        (
            ('div', 'class', 'tab_content'),
            ('footer', None, None),
            None
        )
    ],
    'advanced-threat-research': [
        (
            ('div', 'class', r'r:content.*'),
            ('footer', None, None),
            (
                ('div', 'class', r'r:pagination.*')
            )
        )
    ]}),
    exp_url_ptn=(
        r'r:https?://.*mcafee.com.*(/\?|-digest\.|resource-library|home\.|EOL\.|solutions/|/index\.|microsites/|'
        r'downloads/|events/|threat-center\.|products\.|japan/|\.pdf|partners/|services/|reports\.|catalog/|'
        r'external-link/|all-articles\.|mcafee-labs\.|support/|about/|publications\.|bulletins\.).*'),
    url_ptn=r'r:https?://.*mcafee.com/.+',
    compact=True
)

policy_tmblog04_1 = HTCExtractor({
    'T1': [
        (
            ('div', 'id', r'r:post-\d+'),
            (
                ('div', 'class', r'r:(yarpp-related|banner-widget-area)')
            ),
            (
                ('div', 'class', 'post-meta'),
                ('div', 'class', 'post-comments')
            )
        )
    ]},
    url_ptn=r'r:https?://blog\.trendmicro\.com/[-_+%a-zA-Z0-9]+/?|'
            r'https?://blog\.trendmicro\.com/[-_+%a-zA-Z0-9]+/[-_+%a-zA-Z0-9]+/?',
    exp_url_ptn=r'r:https?://blog\.trendmicro\.com/.*/category/|https?://blog\.trendmicro\.com/category/|'
                r'https?://blog\.trendmicro\.com/.*/tag/|https?://blog\.trendmicro\.com/[-_+%a-zA-Z0-9]+/\d{4}/\d{2}/',
    compact=True
)

policy_securelist05_1 = HTCExtractor({
    'T1': [
        (
            ('div', 'id', 'primary'),
            (
                ('div', 'class', 'entry-footer'),
                ('ul', 'class', 'related-posts'),
                ('h3', 'class', 'widget-title')
            ),
            (
                ('div', 'id', 'authors-wrap'),
                ('div', 'class', r'r:(entry-social|clear entry-meta|entry-meta|author-wrap co-author)'),
                ('div', 'class', 'post-toc toc-container toc-sticky'),
                ('div', 'class', 'uppercase entry-tags')
            )
        )
    ],
    'T2': [
        (('h1', 'class', 'entry-title'), None),
        (
            ('div', 'class', 'entry-content'),
            (
                ('h3', 'class', 'widget-title')
            ),
            (
                ('div', 'id', 'authors-wrap'),
                ('div', 'class', 'uppercase entry-tags'),
                ('div', 'class', r'r:(entry-social|clear entry-meta|entry-meta|author-wrap co-author)'),
                ('div', 'class', 'post-toc toc-container toc-sticky')
            )
        )
    ]},
    url_ptn=r'r:https?://securelist\.com/[-_+%a-zA-Z0-9]+/\d+/?|'
            r'https?://securelist\.com/\d+/[-_+%a-zA-Z0-9]+/?|'
            r'https?://securelist\.com/blog/[-_+%a-zA-Z0-9]+/\d+/[-_+%a-zA-Z0-9]+/?',
    exp_url_ptn=r'r:https?://securelist\.com/threat-category/|'
                r'https?://securelist\.com/.*\?tag=\d+|'
                r'https?://securelist\.com/.*\?category=\d+|'
                r'https?://securelist\.com/.*\?author=.*|'
                r'https?://securelist\.com/.*\?year=\d+&month=\d+',
    compact=True
)

policy_infosecinstitute06_1 = HTCExtractor({
    'T1': [
        (('h1', None, None), None),
        (
            ('section', 'class', r'r:post-col-2-3.*'),
            (
                ('div', 'class', 'bottom-two-box')
            ),
            (
                ('div', 'class', r'r:(intro|pardot form)')
            )
        )
    ],
    'T2': [
        (('h1', None, None), None),
        (
            ('article', 'class', 'post-content'),
            (
                ('div', 'class', 'share vertical'),
                ('section', 'class', r'r:post-author.*'),
            ),
            (
                ('div', 'class', r'r:(intro|pardot form)'),
                ('li', 'class', r'r:(prev|next)')
            )
        )
    ]},
    url_ptn=r'r:https?://resources\.infosecinstitute\.com/category/enterprise/[-_+%a-zA-Z0-9]+/[-_+%a-zA-Z0-9]+/[-_+%a-zA-Z0-9]+/|'
            r'https?://resources\.infosecinstitute\.com/[-_+%a-zA-Z0-9]+/',
    exp_url_ptn=r'r:https?://resources\.infosecinstitute\.com/category/[-_+%a-zA-Z0-9]+/?$|'
                r'https?://resources\.infosecinstitute\.com/.*/page/\d+/?',
    compact=True
)

policy_esecurityplanet07_1 = HTCExtractor({
    'T1': [
        (('h1', 'itemprop', 'name'), None),
        (('?h3', 'id', 'article-leader'), None),
        (
            ('div', 'id', 'article-content'),
            (
                ('div', 'id', r'r:(related_articles|auto-related-article|bottom-container)'),
                ('div', 'id', 'post_comment_form')
            ),
            (
                ('div', 'id', r'r:(article-ads|olal-container|social-sidebar)'),
                ('div', 'id', 'article-ads'),
                ('div', 'class', 'article-byline'),
                ('span', 'id', 'olal-widget-impression-tracker'),
                ('span', 'class', 'widget-title'),
                ('div', 'class', 'related-article')
            )
        )
    ],
    'T2': [
        (
            ('div', 'id', 'breadcrumb-article-title'),
            None,
            ('div', 'class', 'breadcrumb')
        ),
        (('?h3', 'id', 'article-leader'), None),
        (
            ('div', 'id', 'article-content'),
            (
                ('div', 'id', r'r:(related_articles|auto-related-article|bottom-container)')
            ),
            (
                ('div', 'id', r'r:(article-ads|olal-container|social-sidebar)'),
                ('div', 'class', 'article-byline'),
                ('span', 'id', 'olal-widget-impression-tracker')
            )
        )
    ]},
    url_ptn=r'r:https?://www\.esecurityplanet\.com/(amp/)?[-_+.%a-zA-Z0-9]+/[-._+%a-zA-Z0-9]+\.html|'
            r'https?://www\.esecurityplanet\.com/(amp/)?[-_+%a-zA-Z0-9]+/article\.php/[_0-9]+/[-_+%a-zA-Z0-9]+\.htm',
    exp_url_ptn=r'r:https?://www\.esecurityplanet\.com/[-_+%a-zA-Z0-9]+$|https?://www\.esecurityplanet\.com/[-_+%a-zA-Z0-9]+/articles',
    compact=True
)

policy_fsecureblog09_1 = HTCExtractor({
    'blog': [
        (('h1', None, None), None),
        (('article', None, None), None)
    ]},
    url_ptn=r'r:https?://blog\.f-secure\.com/[-_+%a-zA-Z0-9]+/(\?.*)?',
    exp_url_ptn=r'r:https?://blog\.f-secure\.com/category/|'
                r'https?://blog\.f-secure\.com/.*/page/\d+/?|'
                r'https?://blog\.f-secure\.com/tag/',
    compact=True
)

policy_reddit10_1 = HTCExtractor({
    't1': [
        (
            ('div', 'data-test-id', 'post-content'),
            (
                ('span', 'text', r'r:[\d.]+[km]? comments')
            ),
            (
                ('div', 'text', r'r:Posted by u/'),
                ('div', 'text', r'r:^[\d.]+[km]?$')
            )
        ),
    ],
    'zdb': [
        (
            (
                ('div', 'class', 'entry unvoted'),
                (
                    ('div', 'class', 'commentarea'),
                    ('ul', 'class', 'flat-list buttons')
                ),
                (
                    ('div', 'class', 'date'),
                    ('p', 'class', 'tagline ')
                )
            )
        )
    ]},
    url_ptn=r'r:https?://www\.reddit\.com/r/[-_+%a-zA-Z0-9]+/comments/',
    exp_url_ptn=r'r:https?://www\.reddit\.com/r/[-_+%a-zA-Z0-9]+/[-_+%a-zA-Z0-9]+/$',
    compact=True,
    dp_tags=[('p', 'class', 'tagline ')]
)

policy_thecybersecurityplace11_1 = HTCExtractor({
    'blog': [
        (
            ('div', 'class', 'main-content left'),
            (
                ('div', 'class', 'r:(writecomm_link|article-foot)')
            ),
            (
                ('div', 'class', 'article-info')
            )
        )
    ]},
    url_ptn=r'r:https?://thecybersecurityplace\.com/[-_+%a-zA-Z0-9]+/?',
    exp_url_ptn=r'r:https?://thecybersecurityplace\.com/tag/|'
                r'https?://thecybersecurityplace\.com/.*/page/\d+/|'
                r'https?://thecybersecurityplace\.com/category/',
    compact=True
)

policy_arstechnica08_1 = HTCExtractor(OrderedDict({
    'article': [
        (
            ('h1', 'itemprop', 'headline'),
            None,
            None
        ),
        (
            ('h2', 'itemprop', 'description'),
            None,
            None
        ),
        (
            ('div', 'itemprop', 'articleBody'),
            ('div', 'class', 'xrail'),
            (
                ('aside', None, None),
                ('figcaption', 'class', 'caption'),
                ('div', 'class', 'story-sidebar-part-content'),
                ('section', 'id', 'promoted-comments')
            )
        )
    ],
    'amp-article': [
        (
            ('h1', 'class', 'amp-wp-title'),
            None,
            None
        ),
        (
            ('div', 'class', 'amp-wp-article-content'),
            ('footer', 'class', 'amp-wp-article-footer'),
            (
                ('aside', None, None),
                ('figcaption', 'class', 'caption'),
                ('div', 'class', 'story-sidebar-part-content'),
                ('section', 'id', 'promoted-comments')
            )
        )
    ],
    'old-amp-article': [
        (
            ('div', 'class', 'amp-wp-content'),
            ('amp-analytics', None, None),
            (
                ('ul', 'class', 'amp-wp-meta'),
                ('aside', None, None),
                ('figcaption', 'class', 'caption'),
                ('div', 'class', 'story-sidebar-part-content'),
                ('section', 'id', 'promoted-comments')
            )
        )
    ]}),
    url_ptn=r'r:https?://.*arstechnica.com/.+',
    compact=True
)
