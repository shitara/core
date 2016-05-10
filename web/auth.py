
import re
import logging
from core.conf import config, settings
from core.ext.exception import *
from core.db import models
from core.util.dict import propdict

auths = config(settings['application']['auths'])
session = auths.get('session') or {}
secrets = auths.get('secrets') or {}

class Session(object):

    def __init__(self, meta, request, response):
        self.meta = meta
        self.request = request
        self.response = response

    def create(self, user):
        self.response.set_cookie(
            settings['session']['name'], str(user.id),
            secure = False,
            path = '/',
            max_age = settings['session'].get('expire', None),
            )
        return user

    def delete(self):
        self.response.set_cookie(
            settings['session']['name'], '',
            secure = False,
            path = '/',
            )

class RequestContext(object):

    def __init__(self, request, response, user, meta):
        self.request  = request
        self.response = response
        self.user = user
        self.meta = meta
        self.session = Session(meta, request, response)

    def __getattr__(self, name):
        return getattr(
            self.request, name)


def user(meta, request, response):

    def validation(m, current_user):

        if len({ i:v for i,v in (auths.get('administrator') or {}).items()
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
        model = models[session[meta['session']]['model'].capitalize()]
        try:
            current_user = model.objects(id = cookie).first()
        except: pass
        validation(session[meta['session']], current_user)

    if meta.get('secrets'):
        parameters = {}
        for i in secrets[meta['secrets']].get('property') or []:
            parameters[i] = request.params.get(i)
        model = models[secrets[meta['secrets']]['model'].capitalize()]
        current_user = model.objects(**parameters).first()
        validation(secrets[meta['secrets']], current_user)

    return RequestContext(
        request, response, locals().get('current_user', None), meta,
        )