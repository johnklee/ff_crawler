#!/usr/bin/env python3
import os
import sys
from collections import OrderedDict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))   # noqa
from purifier.te_policy import HTCExtractor

policy_databreachtoday02_1 = HTCExtractor(
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
                ('a', 'type', 'button')
            )
        )
    ],
    url_ptn=r'r:https?://\w+\.databreachtoday.com/(?!(events/|surveys/|authors/)).*-[^c]-.+|https?://www.databreachtoday.com/(articles.php|webinars.php|whitepapers.php|handbooks.php|interviews.php)(?!(\?page_cl=)).+',
    compact=True,
    dp_tags=[('p', 'class', 'text-muted')]
)

policy_securityintelligence03_1 = HTCExtractor({
    'T1': [
        (('div', 'class', r'r:post-single.*'), None),
        (('article', 'id', r'r:post-.*'), None, (('div', 'class', 'post-tags'), ('section', 'id', 'new-author-box')))
    ],
    'T2': [
        (('article', 'id', r'r:post-.*'), ('footer', 'id', 'footer'), (('div', 'class', 'post-tags'), ('div', 'class', 'img-source'), ('div', 'class', r'r:post-share.*'), ('section', 'class', 'author-box'), ('section', 'class', 'related-events'), ('div', 'class', 'item featured-article')))
    ],
    'T3': [
        (('h1', 'class', 'ibm-h1'), None),
        (('div', 'class', 'single-content'), None)
    ],
    'online': [
        (
            ('article', 'class', 'single'),
            (
                ('div', 'class', r'r:(single__social-horizontal|single__tags|author-box)'),
            ),
            (
                ('div', 'class', r'r:(single__labels|single__featured-image|single__breadcrumbs)'),
                ('a', 'class', 'btn orange1 large')
            )
        )
    ]},
    url_ptn=r'r:https?://securityintelligence.com/.+',
    exp_url_ptn=r'r:https?://securityintelligence\.com/category/|'
                r'https?://securityintelligence\.com/category/.*/page/\d+/?',
    compact=True
)

policy_nist04_1 = HTCExtractor({
    'T1': [
        (('div', 'id', 'page-content'), ('footer', 'id', 'footer'))
    ],
    'T2': [
        (('div', 'class', 'container'), ('div', 'id', r'r:footer.*'))
    ],
    'T3': [
        (('div', 'id', 'contents'), ('div', 'id', r'r:footer.*'))
    ]},
    url_ptn=r'r:https?://nvd.nist.gov/vuln/detail/CVE-.+|'
            r'https?://web\.nvd\.nist.gov/view/vuln/detail\?vulnId=CVE-.+',
    compact=True
)

policy_govinfosecurity06_1 = HTCExtractor({
    't1': [
        (
            ('article', 'id', 'generic-article'),
            (
                ('ul', 'class', 'topics pull-left'),
                ('div', 'class', 'row nav-articles')
            ),
            (
                ('div', 'class', r'r:share-this-buttons.*'),
                ('span', 'class', 'article-byline')
            )
        ),
    ],
    'zdb': [
        (
            ('article', 'class', r'r:(generic-article|asset single whitepaper|asset webinar-intro|asset asset-img-res|asset blog-article asset-img-res)'),
            (
                ('ul', 'class', 'topics pull-left'),
                ('div', 'class', 'row nav-articles'),
                ('div', 'id', 'topicsBar')
            ),
            (
                ('div', 'class', r'r:share-this-buttons.*'),
                ('span', 'class', 'article-byline'),
                ('div', 'class', 'visible-xs')
            )
        )
    ]},
    url_ptn=r'r:https?://www\.govinfosecurity\.com/[-_+%a-zA-Z0-9]+-a-\d+(/op-\d+)?$|'
            r'https?://www\.govinfosecurity\.com/articles\.php\?art_id=\d+|'
            r'https?://www\.govinfosecurity\.com/press-releases/[-_+%a-zA-Z0-9]+-p-\d+$',
    compact=True,
    dp_tags=[('p', 'class', 'text-muted'), ('figcaption', None, None)],
    ig_tags=['i']
)

policy_govinfosecurity06_2 = HTCExtractor(
    [
        (
            ('article', 'class', r'r:(generic-article|asset single whitepaper|asset webinar-intro|asset asset-img-res|asset blog-article asset-img-res|asset)'),
            (
                ('ul', 'class', 'topics pull-left'),
                ('div', 'class', 'row nav-articles'),
                ('div', 'id', 'topicsBar')
            ),
            (
                ('div', 'class', r'r:share-this-buttons.*'),
                ('span', 'class', 'article-byline'),
                ('div', 'class', 'visible-xs')
            )
        ),
    ],
    url_ptn=r'r:https?://www\.govinfosecurity\.com/whitepapers/[-_+%a-zA-Z0-9]+-w-\d+(\?.*)?$|'
            r'https?://www\.govinfosecurity\.com/webinars/[-_+%a-zA-Z0-9]+-w-\d+(\?.*)?$|'
            r'https?://www\.govinfosecurity\.com/interviews/[-_+%a-zA-Z0-9]+-i-\d+(/op-\d+)?$|'
            r'https?://www\.govinfosecurity\.com/blogs/[-_+%a-zA-Z0-9]+-p-\d+$|'
            r'https?://www\.govinfosecurity\.com/events/[-_+%a-zA-Z0-9]+-e-\d+$|'
            r'https?://www\.govinfosecurity\.com/blogs\.php\?postID=\d+|'
            r'https?://www\.govinfosecurity\.com/whitepapers\.php\?wp_id=\d+',
    compact=True,
    dp_tags=[('p', 'class', 'text-muted'), ('figcaption', None, None)]
)

policy_talosintelligence05_1 = HTCExtractor(
    [
        (
            ('div', 'class', 'r:post hentry.*'),
            ('div', 'class', 'post-footer'),
            None
        )
    ],
    url_ptn=r'r:https?://blog\.talosintelligence\.com/.+',
    exp_url_ptn=r'r:https?://blog\.talosintelligence\.com/\d{4}/?$|'
                r'https?://blog\.talosintelligence\.com/\d{4}/\d{2}/?$|'
                r'https?://blog\.talosintelligence\.com/search/',
    compact=True
)

policy_talosintelligence05_2 = HTCExtractor(
    [
        (
            ('div', 'class', 'r:.*report'),
            ('div', 'class', 'r:.*button_area'),
            None
        )
    ],
    url_ptn=r'r:https?://(?!blog\.).*talosintelligence\.com/(vulnerability_reports/|reports/).+',
    compact=True
)

policy_informationsecuritybuzz07_1 = HTCExtractor({
    'T1': [
        (('h1', 'itemprop', 'headline'), None),
        (
            ('div', 'itemprop', 'articleBody'),
            (
                ('div', 'class', 'article-end')
            ),
            (
                ('div', 'class', 'su-box su-box-style-noise'),
                ('aside', None, None)
            )
        )
    ],
    'T2': [
        (('h1', 'itemprop', 'headline'), None),
        (
            ('div', 'itemprop', 'text'),
            ('div', 'class', 'article-end'),
            ('div', 'class', 'su-box su-box-style-noise')
        )
    ]},
    url_ptn=r'r:https?://(www.)?informationsecuritybuzz.com/(articles|news|expert-comments|study-research)/.+',
    compact=True,
    ig_tags_with_data=['strong', 'b']
)

policy_cuinfosecurity09_1 = HTCExtractor(
    [
        (('article', 'class', r'r:asset.*'), None, (('span', 'class', 'article-byline'), ('div', 'class', r'r:share.*')))
    ],
    url_ptn=r'r:https?://www.cuinfosecurity.com/(?!(authors/|events/|surveys/|handbooks/|whitepapers/)).*-[^c]-.+',
    compact=True,
    dp_tags=[('p', 'class', 'text-muted')],
    ig_tags_with_data=['b']
)

policy_uscert08_1 = HTCExtractor(OrderedDict([
    ('t1', [
        (
            ('h1', 'class', 'title'),
            None,
            None
        ),
        (
            ('article', 'class', 'r:node.*'),
            None,
            (
                ('div', 'id', 'social-options'),
                ('div', 'id', 'document-feedback'),
                ('div', 'class', 'full-copyright')
            )
        )
    ]),
    ('archive', [
        (
            ('article', 'class', 'r:node.*'),
            ('footer', 'id', 'section-footer'),
            (
                ('div', 'id', 'social-options'),
                ('div', 'id', 'document-feedback'),
                ('div', 'class', 'full-copyright'),
                ('div', 'id', r'r:.+-archive'),
                ('a', 'href', r'#top'),
                ('td', 'class', 'tabletext'),
                ('td', 'class', 'csbTocTitle'),
                ('a', 'href', r'r:.*/legal.html')
            )
        )
    ]),
    ('t2', [
        (
            ('h1', 'class', 'title'),
            None,
            None
        ),
        (
            ('div', 'id', 'block-system-main'),
            None,
            (
                ('div', 'class', 'article-listing')
            )
        )
    ]),
    ('t3', [
        (
            ('h1', 'id', 'page-title'),
            None,
            None
        ),
        (
            ('h2', 'id', 'page-sub-title'),
            None,
            None
        ),
        (
            ('div', 'id', 'ncas-content'),
            None,
            None
        )
    ]),
    ('t4', [
        (
            ('h1', 'id', 'page-title'),
            None,
            None
        ),
        (
            ('h2', 'id', 'page-sub-title'),
            None,
            None
        ),
        (
            ('div', 'class', 'content clearfix'),
            ('div', 'id', 'document-feedback'),
            None
        )
    ])]),
    url_ptn=r'r:https://www.us-cert.gov/(?!(about-us$|announcements$|ncas/current-activity$)).+(?<!(\.pdf|\.PDF|\.txt))$',
    compact=True,
    dp_tags=[('p', 'class', 'privacy-and-terms')]
)

policy_eweek10_1 = HTCExtractor(OrderedDict([
    ('t1', [
        (
            ('article', 'class', r'r:col.+'),
            ('ul', 'class', 'story-nav'),
            (
                ('div', 'class', r'r:ntv-box.*'),
                ('div', 'id', r'r:asset-bottom.*'),
                ('div', 'class', 'further-reading'),
                ('div', 'id', 'manual-webinar-asset'),
                ('div', 'class', 'social-actions'),
                ('div', 'class', 'media-box'),
                ('div', 'class', r'r:widget-recent-slides.*'),
                ('div', 'class', 'listing'),
                ('a', 'class', r'r:btn.*'),
                ('ul', 'class', 'pagination')
            )
        )
    ]),
    ('t2', [
        (
            ('h1', 'class', 'blackcolor'),
            None,
            None
        ),
        (
            ('div', 'class', 'article_body'),
            ('div', 'class', 'pagination'),
            None
        )
    ]),
    ('t3', [
        (
            ('div', 'id', 'content'),
            ('div', 'class', 'arti-bottom'),
            (
                ('div', 'class', 'nav'),
                ('div', 'class', 'prev-slide'),
                ('div', 'class', 'item_image'),
                ('div', 'class', 'next-slide'),
                ('div', 'class', 'last_slide')
            )
        )
    ])]),
    url_ptn=r'r:https?://www.eweek.com/.+',
    compact=True
)
