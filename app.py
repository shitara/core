
import falcon
import logging

from core.ext import autoreload
from core.conf import settings, env
from core.ext.process import processes
from core.web.handler import handlers

class API(falcon.API):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.req_options.keep_blank_qs_values = True
        self.req_options.auto_parse_form_urlencoded = True

app = API()

for handler in handlers:
    app.add_route(
        handler[0], handler[1]
        )

logging.info('%s for %s is started to running' % (
    settings['name'], env))

