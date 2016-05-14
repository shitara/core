
from core.conf import settings
from core.ext.exception import RuntimeError
from core.util.dict import propdict
from core.util.importlib import import_attr

import logging

def _(plugin):
    try:
        _plugin = import_attr(
            isinstance(plugin, dict) and plugin['class'] or plugin
            )
        _params = (
            isinstance(plugin, dict) and plugin['arguments'] or {}
            ) or {}
        return dict(
            OrderedDict = lambda c: _plugin(**c),
            dict = lambda c: _plugin(**c),
            list = lambda c: _plugin(*c),
            )[type(_params).__name__](
                _params) if isinstance(_plugin, type) else _plugin
    except ImportError as e:
        RuntimeError(e).throw()

def plugin(name, default):
    item = lambda i, d: (
        item(i+1, d[name[i]]) if i < len(name) else d
        )
    try: return item(0, settings)
    except KeyError as e:
        return default

def dotname(name, data):
    namespaces = name.split('.')
    for v in reversed(namespaces[1:]):
        data = dict({ v: data })
    return (namespaces[0], data)

runtimes = propdict()
for i,v in plugin(['runtime', 'plugins'], {}).items():
    i,v = dotname(i, _(v))
    runtimes[i] = v

responses = propdict()
for i,v in plugin(['response'], {}).items():
    i,v = dotname(i, getattr(_(v), 'emit'))
    responses[i] = v

renderers = propdict()
for i,v in plugin(['renderer', 'plugins'], {}).items():
    i,v = dotname(i, getattr(_(v), 'render'))
    renderers[i] = v

excepts = [
    _(plugin) for plugin in plugin('except', [])
    ]

