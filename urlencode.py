always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                'abcdefghijklmnopqrstuvwxyz'
                '0123456789' '_.-')


def urlencode(query):
    if isinstance(query, dict):
        query = query.items()
    l = []
    for k, v in query:
        if not isinstance(v, list):
            v = [v]
        for value in v:
            k = quote_plus(str(k))
            v = quote_plus(str(value))
            l.append(k + '=' + v)
    return '&'.join(l)


def quote_plus(s):
    if ' ' in s:
        s = s.replace(' ', '+')
    return quote(s)

def quote(s):
    res = []
    replacements = {}
    for c in s:
        if c in always_safe:
            res.append(c)
            continue
        res.append('%%%x' % ord(c))
    return ''.join(res)
