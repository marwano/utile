
from utile import safe_import, PY3
from os.path import dirname, abspath
import unittest
StringIO = __import__('io' if PY3 else 'StringIO').StringIO
Queue = __import__('queue' if PY3 else 'Queue').Queue

TEST_DIR = dirname(abspath(__file__))


def read_file(path):
    with open(path) as f:
        return f.read()


def fallback_patch(*args, **kwds):
    return lambda func: func


class TestCase(unittest.TestCase):
    """TestCase that runs on Python 2 and 3"""

    if not PY3:
        #assertRaisesRegexp renamed to assertRaisesRegex in python 3.2
        def assertRaisesRegex(self, *args, **kwargs):
            return self.assertRaisesRegexp(*args, **kwargs)


# if mock not installed use fallback_patch as an empty decorator
patch = safe_import('mock.patch', fallback_patch)
mock = safe_import('mock')
etree = safe_import('lxml.etree')
Crypto = safe_import('Crypto')
yaml = safe_import('yaml')


# function to convert init to bytes for python 2 and 3
int_to_byte = (lambda x: bytes([x])) if PY3 else chr

suite = unittest.TestLoader().discover(TEST_DIR)
