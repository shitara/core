
class propdict(dict):
    __getattr__ = dict.__getitem__

def deepupdate(d, u):
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = deepupdate(d.get(k, {}), v)
        else:
            d[k] = u[k]
    return d

