#!/usr/bin/env python

import sys
from unittest import TestCase, skipUnless
from subprocess import check_output, CalledProcessError
from utile import safe_import, encrypt, decrypt, shell_quote, flatten
import re
import os.path
Crypto = safe_import('Crypto')

BYTES_ALL = ''.join(map(chr, range(256)))
BYTES_ALL_BUT_NULL = ''.join(map(chr, range(1, 256)))


class BaseTestCase(TestCase):
    @skipUnless(Crypto, 'pycrypto not installed')
    def test_crypto(self):
        pairs = {
            'secret_key': 'some data',
            BYTES_ALL: BYTES_ALL,
        }
        for key, expected in pairs.items():
            actual = decrypt(key, encrypt(key, expected))
            self.assertEqual(expected, actual)

    @skipUnless(os.path.exists('/bin/echo'), '/bin/echo not found')
    def test_shell_quote(self):
        for expected in ['testing...', BYTES_ALL_BUT_NULL]:
            cmd = '/bin/echo -n %s' % shell_quote(expected)
            actual = check_output(cmd, shell=True)
            self.assertEqual(expected, actual)

    def test_flatten(self):
        self.assertEqual(flatten([(0, 1), (2, 3)]), range(4))

    def test_safe_import(self):
        pairs = {
            'os': os,
            'os.path': os.path,
            'os.path.exists': os.path.exists,
            'NoSuchModule': None,
        }
        for name, expected in pairs.items():
            self.assertEqual(safe_import(name), expected)
        self.assertEqual(safe_import('NoSuchModule', 'default'), 'default')

#    def test_dir_dict(self):
        
