
from core.conf import config, settings
from core.util.dict import propdict

class Error(Exception):
    def __init__(self, kwargs):
        self.message = self.message % kwargs

    def throw(self):
        raise self

    def __str__(self):
        return self.message

class RuntimeError(Error):
    def __init__(self, exception):
        self.exception = exception

    def __str__(self):
        return str(self.exception)


errors = propdict()

for k,v in config(settings['application']['errors']).items():
    errors[k] = type(k, (Error,), dict(
        status = v['status'],
        message = v.get('message', '%s'),
        ))
