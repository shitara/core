
from core.conf import settings
from core.ext.exception import RuntimeError
from core.util.dict import propdict
from core.util.importlib import import_attr

import logging

def _(plugin):
    try:
        _plugin = import_attr(
            isinstance(plugin, dict) and plugin['module'] or plugin)
        return not 'arguments' in plugin and _plugin or _plugin(
            **(plugin.get('arguments') or {}))
    except ImportError as e:
        RuntimeError(e).throw()

_plugins = settings.get('plugins')

def dotname(name, data):
    namespaces = name.split('.')
    for v in reversed(namespaces[1:]):
        data = dict({ v: data })
    return (namespaces[0], data)

runtimes = propdict()
for name, plugin in (_plugins.get('runtime') or {}).items():
    name, plugin = dotname(name, _(plugin))
    runtimes[name] = plugin

renders = propdict()
for name, plugin in (_plugins.get('render') or {}).items():
    name, plugin = dotname(name, getattr(_(plugin), 'render'))
    renders[name] = plugin

excepts = [
    _(plugin) for plugin in (_plugins.get('except') or [])
    ]

