
import re

def plural(noun):
    keywords = (
        ('[sxz]$',           lambda n: re.sub('$',  'es',  n), ),
        ('[^aeioudgkprt]h$', lambda n: re.sub('$',  'es',  n), ),
        ('[^aeiou]y$',       lambda n: re.sub('y$', 'ies', n), ),
        )
    for v in keywords:
        if re.search(v[0], noun): return v[1](noun)
    return noun + 's'