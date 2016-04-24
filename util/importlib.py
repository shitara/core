
from importlib import *

def import_attr(modname, default = None):
    try:
        return import_module(modname)
    except ImportError as e:
        modname = modname.split('.')
        module = import_module('.'.join(modname[:-1]))
        return getattr(module, modname[-1], default)