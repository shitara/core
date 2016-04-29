
from core.conf import settings
from core.ext.exception import RuntimeError
from core.util.dict import propdict
from core.util.importlib import import_attr


def _(plugin):
    try:
        _plugin = import_attr(
            isinstance(plugin, dict) and plugin['module'] or plugin)
        return not 'arguments' in plugin and _plugin or _plugin(
            **(plugin.get('arguments') or {}))
    except ImportError as e:
        RuntimeError(e).throw()

_plugins = settings.get('plugins')

runtimes = propdict({
    name:_(plugin) for name, plugin in (_plugins.get('runtime') or {}).items()
    })

renders = propdict({
    name:getattr(_(plugin), 'render') for name, plugin in (_plugins.get('render') or {}).items()
    })

excepts = [
    _(plugin) for plugin in (_plugins.get('except') or [])
    ]

