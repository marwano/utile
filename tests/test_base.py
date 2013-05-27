#!/usr/bin/env python

from unittest import TestCase, skipUnless
from subprocess import check_output
from tempfile import NamedTemporaryFile
from StringIO import StringIO
from os.path import exists
from textwrap import dedent
import datetime
import os.path
import sys
from support import patch, mock, Crypto, pep8, docutils, BASE_DIR
from utile import (
    safe_import, encrypt, decrypt, shell_quote, flatten, dir_dict, mac_address,
    process_name, TemporaryDirectory, file_lock, commands_required, resolve,
    EnforcementError, parse_table)

BYTES_ALL = ''.join(map(chr, range(256)))
BYTES_ALL_BUT_NULL = ''.join(map(chr, range(1, 256)))
IFCONFIG = """\
eth0      Link encap:Ethernet  HWaddr d4:be:d9:a0:18:e1
          inet addr:10.0.0.13  Bcast:10.0.0.255  Mask:255.255.255.0
          inet6 addr: fe80::d6be:d9ff:fea2:f8e1/64 Scope:Link
"""


class BaseTestCase(TestCase):
    @skipUnless(Crypto, 'pycrypto not installed')
    def test_crypto(self):
        pairs = {
            'secret_key': 'some data',
            BYTES_ALL: BYTES_ALL,
        }
        for key, expected in pairs.items():
            actual = decrypt(key, encrypt(key, expected))
            self.assertEqual(actual, expected)

    @skipUnless(exists('/bin/echo'), '/bin/echo not found')
    def test_shell_quote(self):
        for expected in ['testing...', BYTES_ALL_BUT_NULL]:
            cmd = '/bin/echo -n %s' % shell_quote(expected)
            actual = check_output(cmd, shell=True)
            self.assertEqual(actual, expected)

    def test_flatten(self):
        self.assertEqual(flatten([(0, 1), (2, 3)]), range(4))

    def test_resolve(self):
        pairs = {
            'datetime': datetime,
            'datetime.datetime': datetime.datetime,
            'datetime.datetime.now': datetime.datetime.now,
        }
        for name, expected in pairs.items():
            self.assertEqual(resolve(name), expected)
        self.assertRaises(ImportError, resolve, 'non_existent_module')
        self.assertRaises(ImportError, resolve, 'sys.non_existent_attribute')

    def test_safe_import(self):
        pairs = {
            'os': os,
            'os.path': os.path,
            'os.path.exists': exists,
            'NoSuchModule': None,
        }
        for name, expected in pairs.items():
            self.assertEqual(safe_import(name), expected)
        self.assertEqual(safe_import('NoSuchModule', 'default'), 'default')

    def test_dir_dict(self):
        class Dummy(object):
            description = 'this is a dummy'
            _private = 'something private'

        data = dir_dict(Dummy())
        self.assertEqual(data['description'], 'this is a dummy')
        self.assertFalse('_private' in data)
        data = dir_dict(Dummy(), only_public=False)
        self.assertTrue('_private' in data)

    @skipUnless(mock, 'mock not installed')
    def test_mac_address(self):
        with patch('utile.check_output', return_value=IFCONFIG):
            self.assertEqual(mac_address(), 'd4:be:d9:a0:18:e1')

    def test_process_name(self):
        self.assertEqual(process_name(1), ['/sbin/init'])

    def test_temp_dir(self):
        with TemporaryDirectory() as tmp:
            self.assertTrue(exists(tmp))
            file = os.path.join(tmp, 'test.txt')
            with open(file, 'w') as f:
                f.write('test data')
            self.assertEqual(open(file).read(), 'test data')
        self.assertFalse(exists(tmp))

    def test_file_lock(self):
        with NamedTemporaryFile() as f:
            tmp = f.name
        self.assertFalse(exists(tmp))
        with file_lock(tmp):
            self.assertTrue(exists(tmp))
            with self.assertRaisesRegexp(IOError, 'Could not lock'):
                with file_lock(tmp):
                    pass
        self.assertFalse(exists(tmp))

    def test_commands_required(self):
        commands_required('python')
        with self.assertRaisesRegexp(EnforcementError, 'i_dont_exist'):
            commands_required('i_dont_exist')

    @skipUnless(pep8, 'pep8 not installed')
    @skipUnless(mock, 'mock not installed')
    def test_pep8(self):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            style = pep8.StyleGuide(paths=[BASE_DIR])
            errors = style.check_files().total_errors
            msg = '%s pep8 error(s)\n%s' % (errors, mock_stdout.getvalue())
            self.assertFalse(errors, msg)

    @skipUnless(docutils, 'docutils not installed')
    def test_parse_table(self):
        input = dedent("""
            ==========  ==========  ================
            color       hex         rgb
            ==========  ==========  ================
            red 	    #FF0000     rgb(255,0,0)
            green       #00FF00     rgb(0,255,0)
            blue        #0000FF     rgb(0,0,255)
            yellow      #FFFF00     rgb(255,255,0)
            ==========  ==========  ================
        """)
        output = [
            {'color': 'red', 'hex': '#FF0000', 'rgb': 'rgb(255,0,0)'},
            {'color': 'green', 'hex': '#00FF00', 'rgb': 'rgb(0,255,0)'},
            {'color': 'blue', 'hex': '#0000FF', 'rgb': 'rgb(0,0,255)'},
            {'color': 'yellow', 'hex': '#FFFF00', 'rgb': 'rgb(255,255,0)'},
        ]
        self.assertEqual(parse_table(input), output)
