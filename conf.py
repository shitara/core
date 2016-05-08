
import os
import sys
import logging
import yaml
import collections
from core.util.dict import deepupdate

yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: collections.OrderedDict(loader.construct_pairs(node)))

logging.basicConfig(
    format='[%(levelname)s] %(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    )

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
    )

_settings = yaml.load(
    open(os.path.join(BASE_DIR, 'settings.yaml'))
    )

env = os.environ.get('PY_PRODUCTION', 'development')
settings = _settings['configuration']
settings = deepupdate(settings, _settings[env])

sys.path.append(BASE_DIR)

def load_config(path):
    return yaml.load(
        open(path).read()
        )

def create_path(*args):
    path = [BASE_DIR]
    path.extend(list(args))
    return os.path.join(*path)

def config(*args):
    return load_config(
        create_path(*args)
        )
