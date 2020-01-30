import os
from datetime import datetime

_URL_TEMPLATE = '[%s](%s)'
_LATEST_LIMIT = 50

_host = open('CNAME').readline().strip()


def get_latest():
    pages = []
    for cur, _, files in os.walk('./'):
        cur = cur[2:]
        if cur.startswith('.'):
            continue

        for f in files:
            if not f.startswith('__') or not f.endswith('.md') or 'index' in f:
                continue

            
            fullname = cur + '/' + f
            edit_time = os.path.getmtime(fullname)
            pages.append((edit_time, f,  cur + '/' + f[2:]))

    content = '## Latest \n\n|Time|Title|\n|--|--|\n'
    for i in sorted(pages, key=lambda x: x[0], reverse=True)[:_LATEST_LIMIT]:
        edit_time = datetime.fromtimestamp(i[0]).strftime('%Y-%m-%d')
        name = i[1][2:-3]
        content += '|' + _URL_TEMPLATE % (name, i[2]) + '|' + edit_time + '|\n'

    return content + '\n'


def get_navigator(host, path):
    content = _URL_TEMPLATE % (host, 'http://' + host)

    cur = 'http://' + host
    for p in path.split('/'):
        if p:
            cur += '/' + p
            content += ' > ' + _URL_TEMPLATE % (p, cur)

    return content + '\n'


def get_index_and_release_files():
    for cur, dirs, files in os.walk('./'):
        cur = cur.replace('./', '')
        if cur.startswith('.'):
            continue

        navigator = get_navigator(_host, cur)
        content = "## " + navigator

        if cur:
            cur += '/'

        for d in dirs:
            if d.startswith('.'):
                continue
            content += '+ ' + _URL_TEMPLATE % (d, d) + '\n'

        for f in files:
            if not f.startswith('__') or not f.endswith('.md') or 'index' in f:
                continue

            f = f[2:-3]
            content += '+ ' + _URL_TEMPLATE % (f, f) + '\n'

            with open(cur + f + '.md', 'w') as tar:
                tar.write('## ' + f + '\n\n' + navigator + '\n')
                with open(cur + '__' + f + '.md') as src:
                    tar.write(src.read())
                tar.write("\n## The End\n\n")
                tar.write("+ My [github location](https://github.com/GhostZCH/)\n")
                tar.write("+ View Source of this website [GhostZch.github.io](https://github.com/GhostZCH/GhostZch.github.io/)\n")
                tar.write("+ Commit [issues](https://github.com/GhostZCH/GhostZch.github.io/issues) to discuss with me and others\n")

        with open(cur + 'index.md', 'w') as f:
            f.write(content + '\n')


def main():
    get_index_and_release_files()

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
