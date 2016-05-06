
import sys
import traceback
import logging
import falcon
import time

from core.db import models
from core.conf import create_path, config, settings
from core.web.renderer import render, error, document
from core.web.locale import Locale
from core.web import validator, auth
from core.ext.runtime import LuaRuntime
from core.ext.exception import errors, Error
from core.ext import plugin

def loggingrequest(func):
    def _(*args, **kwargs):
        t = time.time()
        r = func(*args, **kwargs)
        logging.info('[%s] %s %s %f' % (
            args[1].method, args[1].relative_uri, args[2].status[:3], time.time() - t)
            )
        return r
    return _

class RequestHandler(object):

    def __init__(self, path, meta, session):
        self.path = path
        self.meta = meta
        self.session = session

    @loggingrequest
    def on_get(self, request, response, **kwargs):
        if request.accept == 'document':
            self.on_document(
                request, response, **kwargs)
        else:
            self.on_request(
                'get', request, response, **kwargs)

    @loggingrequest
    def on_post(self, request, response, **kwargs):
        if request.accept == 'document':
            self.on_document(
                request, response, **kwargs)
        else:
            self.on_request(
                'post', request, response, **kwargs)

    def on_request(self, method, request, response, **kwargs):
        try:
            locale = Locale(request.headers.get(
                'Accept-Language'.upper()) or 'en')

            for i,v in kwargs.items():
                request.params[i] = v
            request = auth.user(
                self.session, request, response)
            request  = validator.query(
                self.meta['request'], request, method)

            modules = [
                create_path(v) for v in self.meta['script']['dependency']
                ]

            data = LuaRuntime(_ = locale.gettext).execute(
                create_path(self.path, 'main.lua'),
                modules = modules,
                properties = dict(
                    models = models,
                    errors = {
                        i:errors[i] for i in (self.meta.get('errors') or [])
                        } if 'errors' in self.meta else errors,
                    ),
                request = request, response = type('', (object,), dict(
                        __getattr__ = lambda self, name: (
                            getattr(response, name) ),
                        redirect = lambda location: falcon.HTTPMovedPermanently(location),
                    ))(),
                )
            render(request, response, locale, self.meta['response'], dict(data))
        except falcon.HTTPStatus as e:
            raise e
        except Exception as e:
            return self.on_exception(e, request, response)

    def on_exception(self, exception, request, response):
        locale = Locale(request.headers.get(
            'Accept-Language'.upper()) or 'en')

        ex, ms, tb = sys.exc_info()
        message = '''\npath: %s\nparams: %s\ncookie: %s\nheaders: %s\nuser: %s\nexception: %s (%s)\ntraceback:%s\n''' % (
            request.path,
            request.params,
            request.cookies,
            request.headers,
            getattr(request, 'user', None) and request.user.id or 'anonymous',
            type(exception), ms,
            ''.join(traceback.format_tb(tb)),)
        logging.error(message)

        try:
            for v in plugin.excepts:
                v.send(exception, message)
        except Exception as e:
            if settings['debug']:
                raise e
            else: logging.error(e)

        if not isinstance(exception, Error):
            exception = errors.InternalServerError(
                'internal server error occurred')

        error(request, response, locale, self.meta['response'], exception)


    def on_document(self, request, response, **kwargs):
        try:
            locale = Locale(request.headers.get(
                'Accept-Language'.upper()) or 'en')

            document(request, response, locale, self.meta)
        except Exception as e:
            return self.on_exception(e, request, response)


handlers = []

for v in config(settings['application']['routes']):
    meta = config(v['handler'], 'meta.yaml')
    handlers.append(
        (v['endpoint'], RequestHandler(v['handler'], meta, dict(
            session = v.get('session'),
            secrets = v.get('secrets'),
            )))
        )


