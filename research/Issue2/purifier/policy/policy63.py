#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))   # noqa
from purifier.te_policy import HTCExtractor


policy_trendmicro01_1 = HTCExtractor({
    'T1': [
        (('h1', 'class', 'lessen_h1'), None),
        (
            ('div', 'class', 'articleContainer'),
            (
                ('section', 'class', 'content-slim-left'),
                ('div', 'class', 'inner-container'),
                ('div', 'class', 'BottomFeedHolder'),
                ('section', 'id', 'social')
            ),
            (
                ('div', 'class', 'articleSidepanel'),
                ('div', 'class', 'footer section')
            )
        )
    ],
    'T2': [
        (('section', 'class', 'artileContent'), (('section', 'class', 'content-slim-left'), ('div', 'class', 'inner-container')), (('ul', 'class', 'sharebuttons')))
    ]},
    url_ptn=r'r:https?://www\.trendmicro\.com/vinfo/[-_+a-z]{2,5}/threat-encyclopedia/malware/[-_+%.a-zA-Z0-9]+',
    exp_url_ptn=r'r:https?://www\.trendmicro\.com/vinfo/[-_+a-z]{2,5}/threat-encyclopedia/search/',
    compact=True
)

policy_trendmicro01_2 = HTCExtractor({
    'T0': [
        (('section', 'class', 'r:articleHeader.*'), ('div', 'id', 'datePub')),
        (('section', 'class', 'content-slim-left'), None)
    ],
    'T1': [
        (('section', 'class', 'r:articleHeader.*'), ('div', 'id', 'datePub')),
        (
            ('section', 'class', 'articleContent'),
            (('div', 'class', 'postedIn'), ('div', 'class', 'imgAttachHolder')),
            (('div', 'class', 'readmorelinkcontainer'), ('a', 'class', 'r:showless.*'))
        )
    ],
    'T2': [
        (
            ('section', 'class', 'artileContent'),
            (('div', 'class', 'postedIn'), ('div', 'class', 'imgAttachHolder')),
            (('div', 'id', 'datePub'), ('ul', 'class', 'sharebuttons'))
        )
    ]},
    url_ptn=r'r:https?://www\.trendmicro\.com/vinfo/[-_+a-z]{2,5}/security/news/[-_+%a-zA-Z0-9]+/[-_+%.a-zA-Z0-9]+',
    compact=True
)

policy_trendmicro01_3 = HTCExtractor({
    'T0': [
        (('section', 'class', 'r:articleHeader.*'), ('div', 'class', 'HolderDateShare')),
        (('section', 'class', 'TEArticle'), ('div', 'class', 'articleSidepanel'), (('div', 'class', 'footer section')))
    ],
    'T1': [
        (
            ('section', 'class', 'artileContent'),
            (('div', 'class', 'postedIn'), ('div', 'class', 'imgAttachHolder'), ('div', 'class', 'articleSidepanel')),
            (('div', 'id', 'datePub'), ('ul', 'class', 'sharebuttons'))
        )
    ]},
    url_ptn=r'r:https?://www\.trendmicro\.com/vinfo/[-_+a-z]{2,5}/threat-encyclopedia/(spam|web-attack)/\d+/[-_+%a-zA-Z0-9]+',
    compact=True
)

policy_trendmicro01_4 = HTCExtractor({
    'T0': [
        (('section', 'class', 'r:articleHeader.*'), ('div', 'class', 'HolderDateShare')),
        (
            ('section', 'class', 'TEArticle'),
            (('div', 'class', 'articleSidepanel'), ('div', 'class', 'BottomFeedHolder')),
            (('div', 'class', 'footer section'))
        )
    ],
    'T1': [
        (
            ('section', 'class', 'artileContent'),
            (
                ('div', 'class', 'postedIn'),
                ('div', 'class', 'imgAttachHolder'),
                ('div', 'class', 'articleSidepanel'),
                ('section', 'class', 'content-slim-left')
            ),
            (('div', 'id', 'datePub'), ('ul', 'class', 'sharebuttons'))
        )
    ]},
    url_ptn=r'r:https?://www\.trendmicro\.com/vinfo/[-_+a-z]{2,5}/threat-encyclopedia/vulnerability/\d+/[-_+%a-zA-Z0-9]+',
    compact=True
)

policy_trendmicro01_5 = HTCExtractor({
    'T0': [
        (('div', 'class', 'textBigbannerHolder'), None, (('h4', None, None))),
        (
            ('div', 'class', 'interactivecontainer'),
            ('section', 'class', 'bottommargintop')
        )
    ],
    'T1': [
        (('section', 'class', 'articleHeader'), ('div', 'class', 'HolderDateShare')),
        (
            ('section', 'class', 'articleContent'),
            (('div', 'class', 'postedIn'), ('div', 'class', 'imgAttachHolder'), ('div', 'class', 'articleSidepanel')),
            (('div', 'id', 'datePub'), ('ul', 'class', 'sharebuttons'), ('section', 'class', 'textMain'))
        )
    ],
    'T3': [
        (
            ('section', 'class', 'artileContent'),
            (('div', 'class', 'postedIn'), ('div', 'class', 'imgAttachHolder'), ('div', 'class', 'articleSidepanel')),
            (('ul', 'class', 'sharebuttons'), ('section', 'class', 'textMain'))
        )
    ]},
    url_ptn=r'r:https?://www\.trendmicro\.com/vinfo/[-_+a-z]{2,5}/security/[-_+%a-zA-Z0-9]+/threat-reports/roundup/[-_+%a-zA-Z0-9]+',
    compact=True
)

policy_trendmicro01_6 = HTCExtractor({
    'T0': [
        (
            ('section', 'role', 'main'),
            None,
            (('ul', 'class', 'sharebuttons'), ('div', 'class', 'inner-container'))
        )
    ]},
    url_ptn=r'r:https?://www\.trendmicro\.com/vinfo/us/threat-encyclopedia/archive/malware/[-_+%.a-zA-Z0-9]+',
    compact=True
)

policy_fsecure02_1 = HTCExtractor({
    'T0': [
        (('div', 'id', 'main-content'), ('section', 'class', 'fs-section bg-blueDarker font-white'))
    ],
    'T1': [
        (
            ('div', 'class', 'container'),
            (('h2', 'class', 'text-center'), ('h2', None, None, 'Submit a Sample'), ('div', 'class', 'desc-publishing p-b-3')),
            (('div', 'id', 'gn'), ('div', 'class', 'col-md-3'), ('div', 'class', 'col-sm-12'), ('div', 'class', 'col-sm-4'), ('div', 'class', 'modal-dialog'))
        )
    ],
    'T2': [
        (('section', None, None), None)
    ]},
    url_ptn=r'r:https?://www\.f-secure\.com/(v-descs|sw-desc)/[-!_+%.a-zA-Z0-9]+\.shtml',
    compact=True
)

policy_fsecure02_2 = HTCExtractor({
    'T0': [
        (('div', 'class', 'modSectionTd2'), None, (('div', 'class', 'modSubHeaderBg')))
    ]},
    url_ptn=r'r:https?://www\.f-secure\.com/weblog/archives/\d+\.html',
    compact=True
)

policy_securityaffairs03 = HTCExtractor(
    [
        (('h1', 'class', 'post_title'), None),
        (
            ('div', 'class', 'post_inner_wrapper'),
            ('div', 'class', 'ssba ssba-wrap'),
            (
                ('h5', 'class', 'share_label'),
                ('div', 'class', 'r:ssba.*'),
                ('div', 'class', 'post_tag'),
                ('div', 'class', 'post_wrapper author'),
                ('h5', 'class', 'share_label'),
                ('div', 'id', 'social_share_wrapper'),
                ('div', 'class', 'post_previous'),
                ('div', 'class', 'post_next'),
                ('div', 'class', 'post_wrapper'),
                ('div', 'class', 'sidebar_wrapper'),
                ('div', 'id', 'post_more_wrapper'),
                ('div', 'class', 'footer_wrapper')
            )
        )
    ],
    url_ptn=r'r:https?://securityaffairs.co/wordpress/\d+/[a-zA-Z]|https?://securityaffairs.co/wordpress/\d+',
    compact=True
)

policy_paloaltonetworks04_1 = HTCExtractor({
    'T1': [
        (('h1', 'class', 'text-white font-weight-black'), None),
        (
            ('div', 'class', 'entry-content'),
            (
                ('footer', None, None)
            ),
            (
                ('td', 'class', r'r:crayon-nums')
            )
        )
    ],
    'T2': [
        (('h1', 'class', 'mb-20 font-weight-light text-white text-center'), None),
        (
            ('div', 'class', 'entry-content'),
            None,
            (
                ('div', 'id', 'comments'),
                ('section', 'class', 'subscribe text-center py-60 pb-30'),
                ('footer', 'class', 'site-footer'),
                ('div', 'class', 'crayon-main')
            )
        )
    ],
    'online': [
        (
            ('div', 'class', 'container'),
            (
                ('div', 'class', r'r:article__subscribe.*'),
                ('footer', None, None)
            ),
            (
                ('ul', 'class', r'r:article__entry-meta.*'),
                ('div', 'class', 'col-sm col-12'),
                ('div', 'id', 'comments'),
                ('footer', 'class', 'site-footer'),
                ('td', 'class', r'r:crayon-nums')
            )
        )
    ]},
    url_ptn=r'r:https?://unit42.paloaltonetworks.com/[a-zA-Z]',
    compact=True
)

policy_paloaltonetworks04_2 = HTCExtractor({
    'T1': [
        (('h1', 'class', 'h2 mb-20 font-weight-ex-bold article-title'), None),
        (
            ('div', 'class', r'r:entry-content.*'),
            (
                ('footer', 'class', 'site-footer')
            ),
            (
                ('div', 'class', r'r:subscribe-form-inner.*')
            )
        )
    ],
    'T2': [
        (('div', 'class', 'post-main'), None, (('div', 'class', 'container'), ('section', 'id', 'comments')))
    ]},
    url_ptn=r'r:https?://researchcenter\.paloaltonetworks\.com/\d{4}/\d{2}/[-_+%a-zA-Z0-9]+/?|'
            r'https?://blog\.paloaltonetworks\.com/\d{4}/\d{2}/[-_+%a-zA-Z0-9]+/?',
    compact=True
)

policy_malwaretips05 = HTCExtractor(
    [
        (('h1', 'class', 'entry-title'), None),
        (('div', 'class', 'entry-content'), ('div', 'class', 'mwt-social'))
    ],
    url_ptn=r'r:https?://malwaretips\.com/blogs/(?!(category/)).+',
    compact=True
)

policy_scmagazine06 = HTCExtractor({
    'online': [
        (('h1', 'class', 'post-heading heading'), None),
        (
            ('div', 'class', 'post-content'),
            None,
            (
                ('section', 'class', 'post-tags')
            )
        )
    ],
    'db': [
        (('h1', 'class', 'title'), None),
        (
            ('div', 'class', 'article-body'),
            (
                ('div', 'class', 'article-insert'),
                ('div', 'class', 'social-share')
            )
        )
    ]},
    url_ptn=r'r:https?://www\.scmagazine\.com/(?!(group-test/|.+/grouptest/|.+/slideshow/|.+/events/|newsletter/|awards/|virtual-conferences/|tr-reviews/|editorial-team/)).+',
    compact=True
)

policy_securityweek07 = HTCExtractor(
    [
        (('h2', 'class', 'page-title'), None),
        (('div', 'class', 'content clear-block'), ('div', 'class', 'ad_in_content'))
    ],
    url_ptn=r'r:https?://www.securityweek.com/(?!(authors/|vendor-directory|mobile-wireless/|cybercrime/)).+',
    compact=True
)

policy_malwarebreakdown09_1 = HTCExtractor({
    'online': [
        (('article', 'id', r'r:post-.*'), ('div', 'id', 'jp-post-flair'), (('div', 'class', 'entry-meta meta-height')))
    ],
    'db1': [
        (('article', 'class', 'amp-wp-article'), None, (('div', 'class', 'sharedaddy sd-sharing-enabled'), ('footer', 'class', 'amp-wp-article-footer')))
    ],
    'db2': [
        (('div', 'class', 'r:article-content.*'), None, (('div', 'class', 'above-entry-meta'), ('div', 'class', 'below-entry-meta'), ('div', 'class', 'sharedaddy sd-sharing-enabled'), ('div', 'class', 'sharedaddy sd-block sd-like jetpack-likes-widget-wrapper jetpack-likes-widget-loaded'))),
    ]},
    url_ptn=r'r:https?://malwarebreakdown\.com/\d{4}/\d{2}/\d{2}/[a-zA-Z]',
    exp_url_ptn=r'r:https?://malwarebreakdown\.com/(tag|category|archives)/',
    compact=True
)

policy_theregister10_1 = HTCExtractor({
    'online': [
        (('div', 'class', 'r:article_head.*'), None),
        (('div', 'id', 'body'), None)
    ],
    'db': [
        (('div', 'id', 'article'), None, (('p', 'class', 'orig-url'), ('p', 'class', 'byline'), ('p', 'class', 'dateline'), ('div', 'id', 'related-stories')))
    ]},
    url_ptn=r'r:https?://www.theregister.co.uk/\d{4}/\d{2}/\d{2}/.*',
    compact=True,
    dp_tags=[('p', 'class', 'byline'), ('p', 'class', 'dateline'), ('p', 'class', 'orig-url')]
)

policy_theregister10_2 = HTCExtractor({
    'online': [
        (('h1', 'class', 'title'), None),
        (('div', 'id', 'body'), None)
    ],
    'db': [
        (('div', 'id', 'article'), None, (('p', 'class', 'orig-url'), ('p', 'class', 'byline'), ('p', 'class', 'dateline'), ('div', 'id', 'related-stories')))
    ]},
    url_ptn=r'r:https?://www.theregister.co.uk/(Print|AMP)/\d{4}/\d{2}/\d{2}/.*',
    compact=True,
    dp_tags=[('p', 'class', 'byline'), ('p', 'class', 'dateline'), ('p', 'class', 'orig-url')]
)
