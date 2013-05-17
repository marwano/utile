
from utile import safe_import
from os.path import dirname

TEST_DIR = dirname(__file__)
BASE_DIR = dirname(TEST_DIR)


def fallback_patch(*args, **kwds):
    return lambda func: func

# if mock not installed use fallback_patch as an empty decorator
patch = safe_import('mock.patch', fallback_patch)
mock = safe_import('mock')
etree = safe_import('lxml.etree')
pep8 = safe_import('pep8')
Crypto = safe_import('Crypto')
