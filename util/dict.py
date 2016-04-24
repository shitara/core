
class propdict(dict):
    __getattr__ = dict.__getitem__