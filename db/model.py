
from core.conf import settings
from core.ext.exception import RuntimeError
from core.util.dict import propdict
from core.util.string import plural
from core.util.importlib import import_attr

from bson import ObjectId

from core.db.column import *
from mongoengine import *

from urllib.parse import urlparse
from datetime import datetime

PROPERTIES = {
    'string':   StringField,
    'text':     StringField,
    'sha256':   Sha256Field,
    'integer':  IntField,
    'float':    FloatField,
    'datetime': DateTimeField,
    'boolean':  BooleanField,
    'binary':   BinaryField,
    'json':     JsonField,
}

REFERENCES = {
    'belongs_to': lambda c: (c, ReferenceField('core.db.models.%s' % c.capitalize())),
    'has_one':    lambda c: (c, ReferenceField('core.db.models.%s' % c.capitalize())),
    'has_many':   lambda c: (plural(c), ListField(ReferenceField('core.db.models.%s' % c.capitalize()))),
}

for i,v in settings['database'].items():
    uri = urlparse(v['uri'])
    connect(
        uri.path.replace('/', ''), host = uri.netloc, alias = i
        )

class ActiveRecord:

    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())

    meta = { 'strict': False }

    def __getitem__(self, name):
        if name in self._fields_ordered:
            return getattr(self, name)
        try:
            return getattr(self, name)
        except AttributeError:
            return getattr(self.__class__.objects, name)

    def validation(self, expression):
        if isinstance(expression, str):
            return eval(expression, {
                i:getattr(self, i) for i in self._fields_ordered
                })
        return False

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def create(cls, kwargs):
        return cls(**kwargs)

    @classmethod
    def update(cls, query, data, upsert = False):
        return cls.query(**query).update(
            **data, upsert = upsert)

    @classmethod
    def find(cls, id):
        if isinstance(id, str):
            return cls.query(id = id).first()
        else:
            return cls.find_by(id)

    @classmethod
    def find_by(cls, kwargs = {}):
        return cls.query(**kwargs)

    @classmethod
    def query(cls, **kwargs):
        query = cls.objects.filter(**{
            attr: value for attr, value in kwargs.items() if not callable(getattr(cls.objects, attr, None))
            })
        for attr, value in kwargs.items():
            if callable(getattr(query, attr, None)):
                query = getattr(query, attr)(value)
        return query

def properties(name, config):
    properties = dict(
        meta = dict (
            db_alias = config.get('database') or 'default',
            collection = plural(config.get('document') or name),
            )
        )

    for name, column in config.get('columns', {}).items():
        prop = column['type'] in PROPERTIES and PROPERTIES[column['type']] or import_attr(
            column['type'], None)
        if not prop:
            RuntimeError('MODEL %s: %s is not defined' % (name, column['type'],)).throw()
        if column.get('property'):
            if column['property'].get('choices'):
                column['property']['choices'] = [
                    isinstance(v, dict) and (i, v) or v for i,v in enumerate(column['property']['choices'])
                    ]

        properties[name] = prop( **(column.get('property') or {}) )

    for name, relationship in (config.get('relationships') or {}).items():
        n, m = REFERENCES[relationship](name)
        properties[n] = m

    return properties

