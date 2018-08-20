import os

URL_TEMPLATE = '+ [%s](%s)\n'


for cur, dirs, files in os.walk('./'):
    cur = cur.replace('./', '')
    if cur.startswith('.'):
        continue

    content = '# > ' + cur + '\n'

    if cur:
        cur += '/'

    for d in dirs:
        if d.startswith('.'):
            continue
        content += URL_TEMPLATE % (d, d)

    for f in files:
        if not f.endswith('.md') or 'index' in f:
            continue

        f = f[:-3]
        content += URL_TEMPLATE % (f, f)

    print content
    with open(cur + 'index.md', 'w') as f:
        f.write(content)

