
from core.conf import settings
from core.ext.exception import RuntimeError

import hashlib
import mongoengine


class Sha256Field(mongoengine.StringField):

    def to_mongo(self, value, **kwargs):
        return super().to_mongo(
            hashlib.sha256(value.encode('utf-8')).hexdigest(), **kwargs)

    def prepare_query_value(self, op, value):
        return super().prepare_query_value(
            op, hashlib.sha256(value.encode('utf-8')).hexdigest())
