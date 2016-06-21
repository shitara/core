
import os
import glob
import logging

from core.conf import create_path, load_config, settings
from core.db.model import ActiveRecord, properties
from core.util.importlib import import_attr
from core.util.dict import propdict

import mongoengine


models = propdict()

for model in glob.glob(create_path(settings['application'].get('models'))):
    name, ext = os.path.splitext(os.path.basename(model))
    config = load_config(model)

    pattern = [
        import_attr(v) for v in config.get('plugins') or []
        ]
    pattern.extend([ActiveRecord, mongoengine.Document])
    model = type(name.capitalize(), tuple(pattern),
        properties(name, config)
        )
    models[name.capitalize()] = model




