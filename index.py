import os

URL_TEMPLATE = '+ [%s](%s)\n'


for cur, dirs, files in os.walk('./'):
    cur = cur.replace('./', '')
    if cur.startswith('.'):
        continue

    if cur:
        cur += '/'

    content = ''

    for d in dirs:
        if d.startswith('.'):
            continue
        d = cur + d
        content += URL_TEMPLATE % (d, d + '/index.html')

    for f in files:
        if not f.endswith('.md') or 'index' in f:
            continue

        f = cur + f[:-3]
        content += URL_TEMPLATE % (f, f + '.html')

    print content
    with open(cur + 'index.md', 'w') as f:
        f.write(content)

