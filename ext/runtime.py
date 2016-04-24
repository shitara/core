
import lupa

from core.db import models
from core.ext.exception import errors
from core.ext.plugin import plugins

from mongoengine import *

class LuaRuntime:

    def __init__(self, **kwargs):
        self.runtime = lupa.LuaRuntime()
        self.property_bind(**kwargs)

    def initialize(self, modules = []):
        self.runtime.execute("package.path = package.path ..';%s'" % ';'.join(modules))
        self.runtime.execute("package.path = package.path ..';%s'" % ';'.join(modules))
        self.property_builtin([
            str, int, float, list, dict, isinstance,
            ])
        self.property_bind(**{
            'models': models,
            'errors': errors,
            })
        self.property_bind(**plugins)

    def execute(self, path, **kwargs):
        self.initialize(kwargs.get('modules') or [])
        self.property_bind(**kwargs)
        with open(path) as f:
            return self.runtime.execute(
                f.read())

    def property_bind(self, **kwargs):
        for k,v in kwargs.items():
            self.runtime.globals()[k] = v

    def property_builtin(self, builtins):
        for v in builtins:
            self.runtime.globals()[v.__name__] = v