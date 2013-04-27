#!/usr/bin/env python

import sys
import unittest
from subprocess import check_output, CalledProcessError
from utile import safe_import, encrypt, decrypt, shell_quote, flatten
from support import Crypto
import re

BYTES_ALL = ''.join(map(chr, range(256)))
BYTES_ALL_BUT_NULL = ''.join(map(chr, range(1, 256)))


class BaseTestCase(unittest.TestCase):
    @unittest.skipIf(not Crypto, 'pycrypto not installed')
    def test_crypto(self):
        pairs = [
            ('secret_key', 'some data'),
            (BYTES_ALL, BYTES_ALL),
            (u'secret_key', u'some data'),
        ]
        for key, data1 in pairs:
            data2 = decrypt(key, encrypt(key, data1))
            self.assertEqual(data1, data2)

    def test_shell_quote(self):
        for data1 in ['testing...', BYTES_ALL_BUT_NULL]:
            data2 = check_output('echo -n %s' % shell_quote(data1), shell=True)
            self.assertEqual(data1, data2)

    def test_flatten(self):
        self.assertEqual(flatten([range(3), range(3, 6)]), range(6))
