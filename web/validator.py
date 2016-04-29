
import re
import logging

from core.util.json import loads
from core.ext.exception import *

def query(meta, request, method):
    if meta.get('method', 'both') != 'both':
        meta['method'] != method.lower() and errors.NotFoundError(
            'wrong request'
            )

    parameters = {}


    for name, param in (meta.get('parameters') or {}).items():
        if 'default' in param:
            request.params[name] = request.params.get(
                name, param.get('default') and str(param['default']) or None
                )
        elif not request.params.get(name):
            errors.ValidationError(
                (param.get('dismiss') or '%s must not be null') % name
                ).throw()
        if param.get('pattern') and request.params[name]:
            if not re.match(param['pattern'], request.params[name]):
                errors.ValidationError(
                    (param.get('dismiss') or '%s is not match pattern') % name
                    ).throw()
        if param.get('convert') and request.params[name]:
            try:
                request.params[name] = dict(
                    string = str, integer = int, float = float, byte = bytes, json = loads,
                    )[param.get('convert')](request.params[name])
            except:
                if not re.match(param['pattern'], request.params[name]):
                    errors.ValidationError(
                        (param.get('dismiss') or '%s is not match pattern') % name
                        ).throw()

        parameters[name] = request.params[name]

    request.params.clear()
    for i,v in parameters.items():
        request.params[i] = v

    return request