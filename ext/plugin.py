
from core.conf import settings
from core.ext.exception import RuntimeError
from core.util.dict import propdict
from core.util.importlib import import_attr


plugins = propdict()

for name, plugin in settings['plugin'].items():
    try:
        _plugin = import_attr(
            isinstance(plugin, dict) and plugin['module'] or plugin)
        plugins[name] = not 'arguments' in plugin and _plugin or _plugin(
            **(plugin.get('arguments') or {}))
    except ImportError as e:
        RuntimeError(e).throw()

excepts = []

for plugin in (settings.get('except') or []):
    try:
        _plugin = import_attr(
            isinstance(plugin, dict) and plugin['module'] or plugin)
        excepts.append(not 'arguments' in plugin and _plugin or _plugin(
            **(plugin.get('arguments') or {})))
    except ImportError as e:
        RuntimeError(e).throw()