#!/usr/bin/env python3
import os
import sys
from collections import OrderedDict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))   # noqa
from purifier.te_policy import HTCExtractor

policy_bleepingcomputer01_1 = HTCExtractor(
    [
        (('div', 'class', 'article_section'), ('div', 'class', 'cz-related-article-wrapp'))
    ],
    url_ptn=r'r:https?://www\.bleepingcomputer\.com/news/[^/]+/[^/]+/?$',
    exp_url_ptn=r'r:https?://www\.bleepingcomputer\.com/news/security/(page/\d+/)?$',
    compact=True
)

policy_bleepingcomputer01_2 = HTCExtractor(
    [
        (('div', 'class', 'cz-top-section'), ('div', 'class', 'cz-review-wrapper')),
        (('div', 'class', 'cz-middle-wrapper'), ('div', 'class', 'cz-vr-disclaimer'), (('div', 'class', 'cz-premium')))
    ],
    url_ptn=r'r:https?://www\.bleepingcomputer\.com/virus-removal/.+',
    exp_url_ptn=r'r:https?://www\.bleepingcomputer\.com/virus-removal/(page/\d+/)?$',
    compact=True
)

policy_sophos02_1 = HTCExtractor({
    't1': [
        (('div', 'class', 'marqTitle'), None), (('div', 'class', 'secondaryContent'), None)
    ],
    't2': [
        (('div', 'class', 'responsive'), None)
    ]},
    url_ptn=r'r:https?://www\.sophos\.com/[a-zA-Z]{2}-[a-zA-Z]{2}/(threat-center|security-news-trends)/.+',
    compact=True
)

policy_sophos02_2 = HTCExtractor({
    't1': [
        (('h1', 'class', 'entry-title'), None),
        (('div', 'class', 'entry-content'), ('div', 'class', 'free-tools-block'))
    ],
    't2': [
        (('h1', 'class', 'amp-wp-title'), None),
        (('div', 'class', 'amp-wp-article-content'), None)
    ]},
    url_ptn=r'r:https?://nakedsecurity\.sophos\.com/\d{4}/\d{2}/\d{2}/.+',
    exp_url_ptn=r'r:https?://nakedsecurity\.sophos\.com/category/',
    compact=True
)

policy_sophos02_3 = HTCExtractor({
    't1': [
        (('h1', 'class', 'entry-title'), None),
        (('div', 'class', 'entry-excerpt'), None),
        (('div', 'class', 'entry-content'), ('ul', 'class', 'block social follow'))
    ],
    't2': [
        (('h1', 'class', 'entry-title'), None),
        (('div', 'class', 'entry-content'), ('ul', 'class', 'block social follow'))
    ]},
    url_ptn=r'r:https?://news\.sophos\.com/[a-zA-Z]{2}-[a-zA-Z]{2}/\d{4}/\d{2}/\d{2}/.+',
    exp_url_ptn=r'r:https?://news\.sophos\.com/[a-zA-Z]{2}-[a-zA-Z]{2}/tag/|'
                r'https?://news\.sophos\.com/[a-zA-Z]{2}-[a-zA-Z]{2}/page/\d+/',
    compact=True
)

policy_sophos02_4 = HTCExtractor(
    [
        (('article', 'id', r'r:post-.*'), ('div', 'id', 'comments'))
    ],
    url_ptn=r'r:https?://nakedsecurity\.sophos\.com/.+/$',
    exp_url_ptn=r'r:https?://nakedsecurity\.sophos\.com/category/',
    compact=True
)

policy_zdnet03_1 = HTCExtractor(
    [
        (('header', 'class', 'storyHeader article'), None, (('div', 'class', 'byline'))),
        (('div', 'class', 'storyBody'), None, (('div', 'class', 'shortcodeGalleryWrapper'), ('a', 'href', r'r:https://www.zdnet.com.*')))
    ],
    url_ptn=r'r:https?://www\.zdnet\.com/article/.+',
    exp_url_ptn=r'r:https?://www\.zdnet\.com/topic/',
    compact=True
)

policy_zdnet03_2 = HTCExtractor(
    [
        (('div', 'id', 'rbContent'), ('div', 'class', 'amp-related-topics'), ('div', 'class', 'relatedContent alignRight'))
    ],
    url_ptn=r'r:https?://www\.zdnet\.com/google-amp/article/.+',
    compact=True
)

policy_zdnet03_3 = HTCExtractor(
    [
        (('h1', 'class', r'r:galleryHeadline.*'), None),
        (('div', 'class', 'details'), None)
    ],
    url_ptn=r'r:https?://www\.zdnet\.com/pictures/.+',
    compact=True
)

policy_computerweekly05 = HTCExtractor({
    't1': [
        (('h1', 'class', r'main-article-title'), None),
        (('h2', 'class', r'main-article-subtitle'), None),
        (
            ('section', 'id', r'content-body'),
            (
                ('section', 'id', 'commenting'),
                ('footer', None, None),
                ('div', 'class', 'latest-body'),
                ('section', 'id', 'commenting-registration')
            ),
            (
                ('div', 'class', r'r:ad-wrapper.*'),
                ('section', 'class', r'r:sign-up-wrapper.*'),
                ('section', 'id', r'r:dig-deeper.*'),
                ('div', 'id', r'content-right'),
                ('div', 'id', 'inlineRegistrationWrapper')
            )
        )
    ],
    't2': [
        (('h1', 'class', r'main-article-title'), None),
        (
            ('section', 'id', r'content-body'),
            (
                ('section', 'id', 'commenting'),
                ('footer', None, None),
                ('div', 'class', 'latest-body'),
                ('section', 'id', 'commenting-registration')
            ),
            (
                ('div', 'class', r'r:ad-wrapper.*'),
                ('section', 'class', r'r:sign-up-wrapper.*'),
                ('section', 'id', r'r:dig-deeper.*'),
                ('div', 'id', r'content-right'),
                ('div', 'id', 'inlineRegistrationWrapper')
            )
        )
    ],
    't3': [
        (
            ('section', 'id', r'content-body'),
            (
                ('section', 'id', 'commenting'),
                ('footer', None, None),
                ('div', 'class', 'latest-body'),
                ('section', 'id', 'commenting-registration')
            ),
            (
                ('div', 'class', r'r:ad-wrapper.*'),
                ('section', 'class', r'r:sign-up-wrapper.*'),
                ('section', 'id', r'r:dig-deeper.*'),
                ('div', 'id', r'content-right'),
                ('div', 'id', 'inlineRegistrationWrapper')
            )
        )
    ]},
    url_ptn=r'r:https?://www\.computerweekly\.com/news/\d+/.*|https?://www.computerweekly.com/feature/[-_+%a-zA-Z0-9]+|'
            r'https?://www\.computerweekly\.com/microscope/news/\d+/.*|https?://www.computerweekly.com/blog/[-_+%a-zA-Z0-9]+/[-_+%a-zA-Z0-9]+|'
            r'https?://www\.computerweekly\.com/(answer|tip|podcast|tutorial)/[-_+%a-zA-Z0-9]+|'
            r'https?://www\.computerweekly\.com/microscope/(feature|report)/[-_+%a-zA-Z0-9]+',
    compact=True
)

policy_blogspot04_1 = HTCExtractor(OrderedDict([
    ('T0', [
        (
            ('article', 'class', r'post-outer-container'),
            (
                ('div', 'class', 'r:post-footer.*'),
                ('div', 'id', 'r:PopularPosts.*'),
                ('div', 'rule', 'feed')
            ),
            (
                ('div', 'class', 'share-buttons-container'),
                ('div', 'class', 'post-header-container container'),
                ('a', 'class', 'twitter-share-button'),
                ('iframe', 'class', 'twitter-share-button')
            )
        )
    ]),
    ('T1', [
        (('h1', 'class', r'r:post-title .*'), None),
        (('div', 'class', r'r:post-body .*'), None)
    ]),
    ('T2', [
        (('h1', 'class', r'r:post-title.*'), None),
        (('div', 'class', r'r:(entry|article-content)'), None)
    ]),
    ('T3', [
        (('h3', 'class', r'r:post-title .*'), None),
        (('div', 'class', r'r:post-body .*'), ('div', 'class', r'r:post-footer\b.*'), (
            ('a', 'class', 'twitter-share-button'),
            ('iframe', 'class', 'twitter-share-button')))
    ]),
    ('T4', [
        (('div', 'class', r'r:post-body .*'), ('div', 'class', r'r:post-footer\b.*'))
    ]),
    ('T5', [
        (('h1', 'class', 'entry-title'), None),
        (('div', 'class', 'entry-content clear'), None)
    ])]),
    url_ptn=r'r:https?://[^/]+.blogspot.com/.+|'
            r'https?://blog\.itsecurityexpert\.co\.uk/\d{4}/\d{2}/[-_+%a-zA-Z0-9]+\.html|'
            r'https?://blog\.[-a-zA-Z0-9]+\.com/\d{4}/\d{2}/[-_+%a-zA-Z0-9]+\.html|'
            r'https?://www\.imperva\.com/blog/[-_+%a-zA-Z0-9]+/?',
    exp_url_ptn=r'r:^https?://blog\.[-a-zA-Z0-9]+\.com/\d{4}/$',
    compact=True
)

policy_healthcareinfosecurity07_1 = HTCExtractor(
    [
        (
            ('div', 'id', r'content'),
            (
                ('div', 'id', 'carousel-three-box'),
                ('div', 'class', 'row nav-articles'),
                ('div', 'id', 'topicsBar')
            ),
            (
                ('span', 'class', 'article-byline'),
                ('div', 'class', r'r:share-this-buttons.*'),
                ('p', 'class', 'text-muted'),
                ('div', 'class', 'visible-xs')
            )
        )
    ],
    url_ptn=r'r:https?://www\.healthcareinfosecurity\.com/(whitepapers|webinars)/[-_+%a-zA-Z0-9]+-w-\d+$|'
            r'https?://www\.healthcareinfosecurity\.com/[-_+%a-zA-Z0-9]+-a-\d+$|'
            r'https?://www\.healthcareinfosecurity\.com/interviews/[-_+%a-zA-Z0-9]+-i-\d+$|'
            r'https?://www\.healthcareinfosecurity\.com/(blogs|press-releases)/[-_+%a-zA-Z0-9]+-p-\d+|'
            r'https?://www\.healthcareinfosecurity\.com/handbooks/[-_+%a-zA-Z0-9]+-h-\d+$|'
            r'https?://www\.healthcareinfosecurity\.com/articles.php\?art_id=\d+$|'
            r'https?://www\.healthcareinfosecurity\.com/webinars.php\?webinarID=\d+$',
    exp_url_ptn=r'r:https?://www\.healthcareinfosecurity\.com/[-_+%a-zA-Z0-9]+-c-\d+(/p-\d+)?$|'
                r'https?://www\.healthcareinfosecurity\.com/blogs/[-_+%a-zA-Z0-9]+-b-\d+(/p-\d+)?$',
    compact=True
)

policy_welivesecurity06_1 = HTCExtractor({
    'online': [
        (('section', 'id', 'article-detail'), ('div', 'class', r'r:similar-articles.*'))
    ],
    'db': [
        (('div', 'class', r'r:wlistingsingle clearfix.*'), None, ('div', 'class', r'r:wlistingsinglesocialmedia.*'))
    ]},
    url_ptn=r'r:https?://www\.welivesecurity\.com/\d{4}/\d{2}/\d{2}/.*',
    exp_url_ptn=r'r:https?://www\.welivesecurity\.com/category/|https?://www\.welivesecurity\.com/.*/page/\d+/?',
    compact=True
)

policy_eset08_1 = HTCExtractor(
    [
        (('h1', 'class', 'title'), None),
        (
            ('div', 'class', 'r:.*article-content.*'),
            ('footer', 'class', 'article-footer'),
            (
                ('span', 'class', 'author'),
                ('a', 'class', 'btn')
            )
        )
    ],
    url_ptn=r'r:https?://www\.eset\.com/(blog/|.+/about/newsroom/|.+/business/resources/).+',
    exp_url_ptn=r'r:https?://www\.eset\.com/blog/listing/type/.*',
    compact=True
)

policy_inforisktoday09_1 = HTCExtractor(
    [
        (
            ('div', 'id', 'content'),
            (
                ('ul', 'class', 'topics pull-left'),
                ('div', 'class', r'r:share-this-buttons  second-bar.*')
            ),
            (
                ('header', 'class', 'header-blog-article'),
                ('div', 'id', 'topicsBar'),
                ('a', 'href', r'r:https?://www.inforisktoday.com.*'),
                ('div', 'class', r'r:share-this-buttons.*'),
                ('span', 'class', 'article-byline'),
                ('div', 'class', 'row nav-articles'),
                ('div', 'id', 'carousel-three-box'),
                ('div', 'id', 'disqus_thread'),
                ('section', 'class', 'about-the-author')
            )
        )
    ],
    url_ptn=r'r:https?://www\.inforisktoday\.com/.*|https?://ca-security.inforisktoday.com/.*|https?://ddos.inforisktoday.com/.*',
    exp_url_ptn=r'r:https?://www\.inforisktoday\.com/.*/[-_+%a-zA-Z0-9]+-c-\d+(/p-\d+)?$',
    compact=True,
    dp_tags=[('p', 'class', 'text-muted')]
)

policy_careersinfosecurity10_1 = HTCExtractor(
    [
        (
            ('article', 'class', 'r:asset.*'),
            (
                ('div', 'id', 'topicsBar'),
                ('div', 'class', 'r:share-this-buttons.+second-bar.*')
            ),
            (
                ('div', 'class', 'r:share-this-buttons.*'),
                ('span', 'class', 'article-byline'),
                ('a', 'type', 'button'),
                ('a', 'href', r'r:https://www.careersinfosecurity.com/.+-c-.+')
            )
        )
    ],
    url_ptn=r'r:https?://www\.careersinfosecurity\.com/(?!(events/|surveys/|authors/)).*-[^c]-.+',
    exp_url_ptn=r'r:https?://www\.careersinfosecurity\.com/[-_+%a-zA-Z0-9]+-c-\d+(/p-\d+)?$',
    compact=True,
    dp_tags=[('p', 'class', 'text-muted')]
)
