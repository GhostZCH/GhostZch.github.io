import os
from datetime import datetime

_URL_TEMPLATE = '[%s](%s)'
_LATEST_LIMIT = 20

_host = open('CNAME').readline().strip()


def get_latest():
    pages = []
    for cur, _, files in os.walk('./'):
        cur = cur[2:]
        if cur.startswith('.'):
            continue

        for f in files:
            if not f.endswith('.md') or 'index' in f:
                continue

            fullname = cur + '/' + f
            edit_time = os.path.getmtime(fullname)
            pages.append((edit_time, f, fullname))

    content = '## Latest \n\n|Time|Title|\n|--|--|\n'
    for i in sorted(pages, key=lambda x: x[0], reverse=True)[:_LATEST_LIMIT]:
        edit_time = datetime.fromtimestamp(i[0]).strftime('%Y-%m-%d %H:%M:%S')
        name = i[1][:-3]
        content += '|' + edit_time + '|' + _URL_TEMPLATE % (name, i[2]) + '|\n'

    return content + '\n'


def get_navigator(host, path):
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

        content = get_navigator(_host, cur)

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
            f.write(content + '\n')


def main():
    get_index_files()

    with open('index.md', 'a') as f:
        with open('highlight.mdx') as src:
            f.write(src.read())

    with open('index.md', 'a') as f:
        f.write(get_latest())

    with open('index.md', 'a') as f:
        with open('end.mdx') as src:
            f.write(src.read())

if __name__ == '__main__':
    main()
