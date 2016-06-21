
import sys
import traceback
import logging
import falcon
import time

from core.db import models
from core.conf import create_path, config, settings
from core.web import renderer, validator
from core.web.locale import Locale
from core.ext import plugin
from core.ext.runtime import LuaRuntime
from core.ext.exception import errors, Error

def loggingrequest(func):
    def _(*args, **kwargs):
        t = time.time()
        r = func(*args, **kwargs)
        logging.info('[%s] %s %s [%s] %f' % (
            args[1].method, args[1].relative_uri, args[2].status[:3], ','.join(
                args[1].access_route), time.time() - t)
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

    @loggingrequest
    def on_options(self, request, response, *kwargs):
        renderer.options(
            request, response, self.meta
            )

    def on_request(self, method, request, response, **kwargs):
        try:
            locale = Locale(request.headers.get(
                'Accept-Language'.upper()) or 'en')

            request.params.update(kwargs)

            request, user, session = validator.authenticate(
                self.session, request, response
                )
            request = validator.parameters(
                self.meta['request'], request, method
                )

            data = LuaRuntime(_ = locale.gettext).execute(
                create_path(self.path, 'main.lua'),
                modules = [ create_path(v) for v in self.meta['dependency'] ],
                properties = dict(
                    models = models,
                    errors = {
                        i:errors[i] for i in (self.meta.get('errors') or [])
                        } if 'errors' in self.meta else errors,
                    ),
                request  = type('', (object,), dict(
                    __getattr__ = lambda self, name: getattr(request, name),
                    meta = self.meta,
                    user = user,
                    session = session,
                    ))(),
                response = type('', (object,), dict(
                    __getattr__ = lambda self, name: getattr(response, name),
                    redirect  = lambda self, location: (
                        (_ for _ in ()).throw(falcon.HTTPMovedPermanently(location))
                        ),
                    broadcast = lambda self, name, value, option = dict(): (
                        plugin.responses['broadcast'](
                            renderer.render(
                                locale, self.meta['broadcast'][name], value
                                ), option)
                        ),
                    meta = self.meta,
                    ))(),
                )
            renderer.response(
                request, response, locale, self.meta['response'], dict(data)
                )
        except falcon.HTTPStatus as e:
            raise e
        except Exception as e:
            return self.on_exception(e, request, response)

    def on_exception(self, exception, request, response):
        locale = Locale(request.headers.get(
            'Accept-Language'.upper()) or 'en')

        ex, ms, tb = sys.exc_info()
        message = '''\npath: %s\nparams: %s\ncookie: %s\nheaders: %s\nuser: %s\naddress: %s\nexception: %s (%s)\ntraceback:%s\n''' % (
            request.path,
            request.params,
            request.cookies,
            request.headers,
            getattr(request, 'user', None) and request.user.id or 'anonymous',
            ','.join(request.remote_addr),
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

        renderer.error(
            request, response, locale, self.meta['response'], exception
            )


    def on_document(self, request, response, **kwargs):
        try:
            locale = Locale(request.headers.get(
                'Accept-Language'.upper()) or 'en')

            renderer.document(
                request, response, locale, self.meta
                )
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


