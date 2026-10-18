# Builds preview.html (Claude preview) and public/index.html (live site) from src/home.html
ring=open('ring.txt').read().strip()
body=open('src/home.html',encoding='utf-8').read().replace('RING',ring)
open('preview.html','w',encoding='utf-8').write(body)
cut=body.index('</style>')+len('</style>')
html=('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
      '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
      + body[:cut] + '\n</head>\n<body>\n' + body[cut:] + '\n</body>\n</html>\n')
open('public/index.html','w',encoding='utf-8').write(html)
print('built', len(html))
