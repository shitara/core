
import lupa
import logging

from core.conf import settings
from core.ext.plugin import runtimes

from mongoengine import *


class LuaRuntime:

    def __init__(self, **kwargs):
        self.runtime = lupa.LuaRuntime()
        self.property_bind(**kwargs)

    def initialize(self, properties, modules = []):
        self.runtime.execute("package.path = package.path ..';%s'" % ';'.join(modules))
        self.runtime.execute("package.path = package.path ..';%s'" % ';'.join(modules))
        self.property_builtin([
            str, int, float, list, dict, repr,
            isinstance,
            ])
        self.property_bind(**properties)
        self.property_bind(**runtimes)

    def execute(self, path, **kwargs):
        self.initialize(kwargs['properties'], kwargs['modules'])
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