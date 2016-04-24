
import os
import csv
import glob

from core.conf import create_path, settings
from core.util.dict import propdict


locales = propdict()

for locale in glob.glob(create_path(settings['application'].get('locales') or '', '*.csv')):

    name, ext = os.path.splitext(os.path.basename(locale))

    with open(locale, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)

        locales[name] = {
            row[0]:row[1] for row in reader
        }

class Locale(object):

    def __init__(self, language):
        for l in language.split(';'):
            for l in l.split(','):
                if l in locales:
                    self.locale = locales[l]
                    return

    def gettext(self, key):
        return self.locale.get(key, key)

    def ngettext(self, key):
        return self.locale.get(
            key, key)