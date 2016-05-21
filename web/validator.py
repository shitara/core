
import re
import logging
from datetime import datetime

from core.util.json import loads
from core.ext.exception import *
from core.db import models
from core.util.dict import propdict

__confs = config(settings['application']['auths'])
__auths = propdict(
    session = __confs.get('session') or {},
    secrets = __confs.get('secrets') or {},
    )

def authenticate(meta, request, response):

    def validation(m, current_user):

        if __confs.get('administrator'):
            if len({ i:v for i,v in __confs['administrator'].items()
                if request.headers.get(i) != v }) == 0:
                return True

        current_user or errors.AuthenticateError(
            'no user').throw()

        for v in m.get('validation') or []:
            current_user.validation(v) or errors.AuthenticateError(
                'no user').throw()
        for i, v in (m.get('header') or {}).items():
            request.headers.get(i) == v or errors.AuthenticateError(
                'no user').throw()
        return False

    current_user = None

    if meta.get('session'):
        cookie = request.cookies.get(settings['session']['name'])
        model = models[__auths.session[meta['session']]['model'].capitalize()]
        try:
            current_user = model.objects(id = cookie).first()
        except: pass
        validation(__auths.session[meta['session']], current_user)

    if meta.get('secrets'):
        parameters = {}
        for i in __auths.secrets[meta['secrets']].get('property') or []:
            parameters[i] = request.params.get(i)
        model = models[__auths.secrets[meta['secrets']]['model'].capitalize()]
        current_user = model.objects(**parameters).first()
        validation(__auths.secrets[meta['secrets']], current_user)

    return (
        request, locals().get('current_user'), type('', (object,), dict(
            create = lambda u: (response.set_cookie(
                settings['session']['name'], str(u.id),
                secure = False,
                path = '/',
                max_age = settings['session'].get('expire', None),
                )),
            delete = lambda: (response.set_cookie(
                settings['session']['name'], '',
                secure = False,
                path = '/',
                ))
            )),
        )

def parameters(meta, request, method):
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
                    string   = str,
                    integer  = int,
                    float    = float,
                    byte     = bytes,
                    json     = loads,
                    boolean  = lambda c: c in ['true', '1'],
                    datetime = lambda c: datetime.strptime(c, '%Y-%m-%d %H:%M:%S')
                    )[param.get('convert')](request.params[name])
            except Exception as e:
                if param.get('pattern') and request.params[name]:
                    if not re.match(param['pattern'], request.params[name]):
                        errors.ValidationError(
                            (param.get('dismiss') or '%s is not match pattern') % name
                            ).throw()

        parameters[name] = request.params[name]

    request.params.clear()
    for i,v in parameters.items():
        request.params[i] = v

    return request