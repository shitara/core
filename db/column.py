
from core.conf import settings
from core.util import json
from core.ext.exception import RuntimeError

import hashlib
import mongoengine
import logging


class Sha256Field(mongoengine.StringField):

    def to_mongo(self, value, **kwargs):
        return super().to_mongo(
            hashlib.sha256(value.encode('utf-8')).hexdigest(), **kwargs)

    def prepare_query_value(self, op, value):
        return super().prepare_query_value(
            op, hashlib.sha256(value.encode('utf-8')).hexdigest())


class JsonField(mongoengine.StringField):

    def to_python(self, value):
        return json.loads(value) if isinstance(value, str) else value

    def validate(self, value):
        try:
            json.dumps(value)
        except:
            super().validate(value)

    def to_mongo(self, value, **kwargs):
        return super().to_mongo(
            json.dumps(value), **kwargs)