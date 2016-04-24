
import sys

from urllib import parse, request

def shell(action, **kwargs):
    return request.urlopen(
        action, parse.urlencode(kwargs).encode('utf-8')
        )

if __name__ == '__main__':
    globals().get(sys.argv[1], lambda *argv: None)(
        sys.argv[2], **dict(
            map(lambda x: x.split('='), len(sys.argv) > 4 and sys.argv[3:] or [])
            )
        )