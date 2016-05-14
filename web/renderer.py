
import os
import yaml
import re
import logging

import jinja2

from core.conf import settings
from core.util.json import dumps, loads
from core.ext.plugin import renderers
from dicttoxml import dicttoxml

TYPES = dict(
    text = lambda c: str(c),
    json = lambda c: dumps(c),
    xml  = lambda c: dicttoxml(c, attr_type=False).decode('utf-8'),
)
TYPES.update(renderers)

class Undefined(jinja2.Undefined):
    def operate(self, *args, **kwargs):
        return self.__class__()

    __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
    __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = __mod__ = \
    __rmod__ = __pos__ = __neg__ = __call__ = __getitem__ = __lt__ = \
    __le__ = __gt__ = __ge__ = __int__ = __float__ = __complex__ = __pow__ = \
    __rpow__ = __getattr__ = operate

environment = jinja2.Environment(
    undefined=Undefined, extensions=['jinja2.ext.i18n'])
environment.filters['json'] = lambda v: isinstance(v, str) and loads(v) or v


def __append_headers(request, response, meta, body = ''):

    response.body = body.replace('<break>', '\\n')
    response.content_type = 'application/%s' % meta['type']

    response.set_header('Access-Control-Allow-Credentials', 'true')

    if settings.get('allow-origin'):
        response.set_header('Access-Control-Allow-Origin',
             request.headers.get('ORIGIN', '') if settings['allow-origin'] == True else settings['allow-origin']
             )
    else:
        response.set_header('Access-Control-Allow-Origin', ' '.join(
            settings.get('allow-origins') or []
            ))
    for i,v in (meta.get('headers') or {}).items():
        response.set_header(i, v)


def render(locale, meta, data, parse = True):
    environment.filters['h'] = lambda v,c: (
        isinstance(v, str) and '\'%s\'' % v.replace('\n', '<break>') or v != None and v or ''
        )
    environment.install_gettext_translations(locale)

    document = environment.from_string(meta['format']).render(
        **data)

    document = yaml.load(document)

    return TYPES[meta['type']](document) if parse else document


def response(request, response, locale, meta, data):

    environment.filters['h'] = lambda v,c: (
        isinstance(v, str) and '\'%s\'' % v.replace('\n', '<break>') or v != None and v or ''
        )
    environment.install_gettext_translations(locale)

    document = environment.from_string(meta['format']).render(
        **data)

    document = yaml.load(document)

    body = TYPES[meta['type']](document)

    response.status = '%d %s' % (200, 'OK')
    __append_headers(request, response, meta, body)


def error(request, response, locale, meta, error):

    environment.filters['h'] = lambda v,c: (
        isinstance(v, str) and '\'%s\'' % v.replace('\n', '<break>') or v != None and v or ''
        )
    environment.install_gettext_translations(locale)

    document = environment.from_string(error.format).render(
        error = error)

    document = yaml.load(document)

    body = TYPES[meta['type']](document)
    response.status = '%d %s' % (getattr(error, 'status', 500), 'NG')
    __append_headers(request, response, meta, body)


def document(request, response, locale, meta):

    environment.filters['h'] = lambda v,c: c
    environment.install_gettext_translations(locale)

    document = environment.from_string(
        re.sub('\{%.+?\%}', '', meta['response']['format']).replace('[]', '')
        ).render()

    document = yaml.load(document)

    data = dict(
        endpoint = request.path,
        title = meta.get('title'),
        description = meta.get('description'),
        request = dict(
            method = meta['request'].get('method') or 'both',
            params = [
                dict(
                    name     = i,
                    comment  = v.get('comment'),
                    required = not 'default' in v,
                    default  = v.get('default'),
                    ) for i,v in (meta['request'].get('parameters') or {}).items()
                ]
            ),
        response = dict(
            type = meta['response']['type'],
            success = document,
            )
        )

    body = TYPES[meta['response']['type']](data)
    __append_headers(request, response, meta['response'], body)


