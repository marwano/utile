
from utile import safe_import
from functools import wraps


def fallback_patch(*args, **kwds):
    return lambda func: func

# if mock not installed use fallback_patch as a dummy decorator
patch = safe_import('mock.patch', fallback_patch)
mock = safe_import('mock')
lxml = safe_import('lxml')
Crypto = safe_import('Crypto')
