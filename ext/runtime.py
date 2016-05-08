
import lupa
import logging

from core.conf import settings
from core.ext.plugin import runtimes

from mongoengine import *


preset = '''
table.filter = function(t, filter)
    local dic = {}
    for k, v in table.iter(t) do
        if type(filter) == 'function' then
            if filter(t[k], k, t) then dic[k] = t[k] end
        elseif type(filter) == 'table' then
            if _(k, filter) then dic[k] = t[k] end
        else
            if t[k] then dic[k] = t[k] end
        end
    end
    return dic
end
table.iter = function(t)
    local dic = {}
    if isinstance(t, dict) then
        return python.iterex(t)
    elseif isinstance(t, list) then
        return python.enumerate(t)
    elseif type(t, list) == 'userdata' then
        return python.enumerate(t)
    else
        return pairs(t)
    end
end
string.split = function(str, delim)
    if string.find(str, delim) == nil then
        return { str }
    end
    local result = {}
    local pat = "(.-)" .. delim .. "()"
    local lastPos
    for part, pos in string.gfind(str, pat) do
        table.insert(result, part)
        lastPos = pos
    end
    table.insert(result, string.sub(str, lastPos))
    return result
end
'''

class LuaRuntime:

    def __init__(self, **kwargs):
        self.runtime = lupa.LuaRuntime()
        self.property_bind(**kwargs)

    def initialize(self, properties, modules = []):
        self.runtime.execute(
            'package.path = package.path ..\';%s\'\n%s' % (';'.join(modules), preset)
            )
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