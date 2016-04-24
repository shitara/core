import re
import json
import datetime
import lupa

class JSONDecoder(json.JSONDecoder):
    pass

class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(o)

    def encode(self, o, *argv, **kwargs):
        return super().encode(
            o, *argv, **kwargs
            )

def loads(s, *argv, **kwargs):
    return JSONDecoder().decode(s, *argv, **kwargs)

def dumps(o, *argv, **kwargs):
    return JSONEncoder().encode(
        _decode(o), *argv, **kwargs)

def _decode(o):
    return dict(
        table = lambda c: dict(c),
        ).get(lupa.lua_type(o), lambda o: o)(o)