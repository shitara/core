
from core.conf import settings
from core.ext.exception import RuntimeError
from core.util.dict import propdict
from core.util.importlib import import_attr

processes = []

for plugin in (settings.get('process') or []):
    try:
        _plugin = import_attr(plugin['class'])
        processes.append(not 'arguments' in plugin and _plugin or _plugin(
            **(plugin.get('arguments') or {})).start())
    except ImportError as e:
        RuntimeError(e).throw()