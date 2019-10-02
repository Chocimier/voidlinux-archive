#!/usr/bin/env python3
import collections
import json
import re
import sys
from email.header import decode_header as email_decode_header
from email.utils import parsedate_to_datetime

from genshi.template import TemplateLoader

posts = []
for i in sys.argv[1:]:
    posts += json.loads(open(i, 'rb').read())
loader = TemplateLoader(['.', 'tools'])
template = loader.load('thread.genshi')
MAIL_FOOTER = re.compile(r'\s+--\s+You are receiving this because.+\s+' +
    r'(View it on GitHub:\s+' +
    r'https://github\.com/voidlinux/[-a-z]+/\w+/\d+\S+\s*$|'
    r'Reply to this email directly or view it on GitHub:\s+' +
    r'https://github\.com/voidlinux/[-a-z]+/\w+/\d+\S+\s*$)')
threads = collections.defaultdict(dict)

def thread_id(post):
    return ((post.get('References') or post['Message-ID'])
        .partition('/')[-1]
        .partition('@')[0]
        .replace('/', ':')
        )

def decode_header(header):
    def to_str(x):
        try:
            return x[0].decode(x[1] or 'ascii')
        except AttributeError:
            return x[0]
    return ''.join(to_str(i) for i in email_decode_header(header))

for post in posts:
    post['From'] = decode_header(post['From']).partition('<')[0].strip()
    post['body'] = MAIL_FOOTER.sub('', post['body'])
    threads[thread_id(post)][post['Message-ID']] = post

threads = {no: list(posts.values()) for no, posts in threads.items()}

for posts in threads.values():
    posts.sort(key=lambda x: parsedate_to_datetime(x['Date']))
    print(template
            .generate(posts=posts)
            .render('xhtml')
            , file=open('{}.html'.format(thread_id(posts[0])), 'w'))

print(loader
        .load('index.genshi')
        .generate(threads=threads)
        .render('xhtml')
        , file=open('index.html', 'w'))
