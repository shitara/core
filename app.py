
import falcon
import logging

from core.ext import autoreload
from core.conf import settings
from core.ext.process import processes
from core.web.handler import handlers

app = falcon.API(middleware=[])

for handler in handlers:
    app.add_route(
        handler[0], handler[1]
        )

logging.info('%s is started to running' % (
    settings['name']))
