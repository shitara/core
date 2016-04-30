
import os
import yaml
import re

import jinja2

from core.conf import settings
from core.util.json import dumps
from core.ext.plugin import renders
from dicttoxml import dicttoxml

TYPES = dict(
    text = lambda c: str(c),
    json = lambda c: dumps(c),
    xml  = lambda c: dicttoxml(c, attr_type=False),
)
TYPES.update(renders)

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

def __append_headers(response, meta, body):

    response.body = body.replace('<break>', '\\n')
    response.content_type = 'application/%s' % meta['type']

    response.set_header('Access-Control-Allow-Credentials', 'true')
    response.set_header('Access-Control-Allow-Origin', ' '.join(
        settings.get('allow-origins') or []))
    for i,v in (meta.get('headers') or {}).items():
        response.set_header(i, v)

def render(request, response, locale, meta, data):

    environment.filters['h'] = lambda v,c: str(v).replace('\n', '<break>')
    environment.install_gettext_translations(locale)

    document = environment.from_string(meta['format']).render(
        **data)

    document = yaml.load(document)

    body = TYPES[meta['type']](document)

    response.status = '%d %s' % (200, 'OK')
    __append_headers(response, meta, body)

def error(request, response, locale, meta, error):

    environment.filters['h'] = lambda v,c: str(v).replace('\n', '<break>')
    environment.install_gettext_translations(locale)

    document = environment.from_string(error.format).render(
        error = error)

    document = yaml.load(document)

    body = TYPES[meta['type']](document)
    response.status = '%d %s' % (getattr(error, 'status', 500), 'NG')
    __append_headers(response, meta, body)

def document(request, response, locale, meta):

    environment.filters['h'] = lambda v,c: c
    environment.install_gettext_translations(locale)

    document = environment.from_string(
        re.sub('\{%.+?\%}', '', meta['response']['format'])
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
    __append_headers(response, meta['response'], body)



