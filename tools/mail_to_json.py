#!/usr/bin/env python3
import json
import mailbox
import sys

HEADERS = (
    'Date',
    'From',
    'Message-ID',
    'References',
    'Subject',
)
try:
    path = sys.argv[1]
except IndexError:
    print('pass path to mbox or maildir as first argument')
    exit(1)

try:
    box = mailbox.mbox(path, None, False)
except IsADirectoryError:
    box = mailbox.Maildir(path, None, False)

box.lock()

try:
    result = []
    for message in box:
        post = {}
        if message['Subject'] and '[voidlinux/' in message['Subject']:
            for header in HEADERS:
                if header in message:
                    post[header] = message[header]
            body = message
            while body.is_multipart():
                body = body.get_payload(0)
            post['body'] = body.get_payload()
            result.append(post)
    print(json.dumps(result, indent=0))
finally:
    box.unlock()
