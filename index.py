import os
from datetime import datetime

_URL_TEMPLATE = '[%s](%s)'
_LASTEST_LIMIT = 20

_host = open('CNAME').readline().strip()

def get_lastest():
    all = []
    for cur, _, files in os.walk('./'):
        cur = cur[2:]
        if cur.startswith('.'):
            continue

        for f in files:
            if not f.endswith('.md') or 'index' in f:
                continue

            fullname = cur + '/' + f
            mtime = os.path.getmtime(fullname)
            all.append((mtime, f, fullname))

    content = '## Lastest \n'
    for i in sorted(all, key=lambda x: x[0], reverse=True)[:_LASTEST_LIMIT]:
        mtime = datetime.fromtimestamp(i[0]).strftime('%Y-%m-%d')
        name = i[1][:-3] + " " + mtime
        content += '+ ' + _URL_TEMPLATE % (name, i[2]) + '\n'

    return content


def get_navegater(host, path):
    content = '## ' + _URL_TEMPLATE % (host, 'http://' + host)

    cur = 'http://' + host
    for p in path.split('/'):
        if p:
            cur += '/' + p
            content += ' > ' + _URL_TEMPLATE % (p, cur)

    return content + '\n'


def get_index_files():
    for cur, dirs, files in os.walk('./'):
        cur = cur.replace('./', '')
        if cur.startswith('.'):
            continue

        content = get_navegater(_host, cur)

        if cur:
            cur += '/'

        for d in dirs:
            if d.startswith('.'):
                continue
            content += '+ ' + _URL_TEMPLATE % (d, d) + '\n'

        for f in files:
            if not f.endswith('.md') or 'index' in f:
                continue

            f = f[:-3]
            content += '+ ' + _URL_TEMPLATE % (f, f) + '\n'

        with open(cur + 'index.md', 'w') as f:
            f.write(content)

get_index_files()

with open('index.md', 'a') as f:
    f.write(get_lastest())

with open('index.md', 'a') as f:
    with open('index.mdx') as src:
        f.write(src.read())
