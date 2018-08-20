import os

URL_TAMPLATE = '[%s](%s)'

for cur, dirs, files in os.walk('./'):
    cur = cur.replace('./', '')
    if cur.startswith('.'):
        continue

    for d in dirs:
        print URL_TAMPLATE % (cur + d, cur + d + '/index.html')
