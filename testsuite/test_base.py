#!/usr/bin/env python

from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from os.path import exists
from glob import glob
import datetime
import os.path
import sys
from testsuite.support import (
    BASE_DIR, patch, mock, Crypto, pep8, StringIO, TestCase, int_to_byte,
    unittest
)
from utile import (
    safe_import, encrypt, decrypt, shell_quote, flatten, dir_dict, mac_address,
    process_name, get_pid_list, TemporaryDirectory, file_lock,
    requires_commands, resolve, EnforcementError, parse_table, force_print,
    reformat_query, raises
)

IFCONFIG = b"""\
eth0      Link encap:Ethernet  HWaddr d4:be:d9:a0:18:e1
          inet addr:10.0.0.13  Bcast:10.0.0.255  Mask:255.255.255.0
          inet6 addr: fe80::d6be:d9ff:fea2:f8e1/64 Scope:Link
"""


class BaseTestCase(TestCase):
    @unittest.skipUnless(Crypto, 'pycrypto not installed')
    def test_crypto(self):
        BYTES_ALL = b''.join(map(int_to_byte, range(256)))

        pairs = {
            b'secret_key': b'some data',
            BYTES_ALL: BYTES_ALL,
        }
        for key, expected in pairs.items():
            actual = decrypt(key, encrypt(key, expected))
            self.assertEqual(actual, expected)

    @unittest.skipUnless(exists('/bin/echo'), '/bin/echo not found')
    def test_shell_quote(self):
        full_ascii = ''.join(map(chr, range(1, 128)))
        for input in ['testing...', full_ascii]:
            cmd = '/bin/echo -n %s' % shell_quote(input)
            process = Popen(cmd, stdout=PIPE, shell=True)
            output = process.communicate()[0].decode('utf8')
            self.assertEqual(input, output)

    def test_flatten(self):
        self.assertEqual(flatten([(0, 1), (2, 3)]), [0, 1, 2, 3])

    def test_resolve(self):
        pairs = {
            'datetime': datetime,
            'datetime.datetime': datetime.datetime,
            'datetime.datetime.now': datetime.datetime.now,
            (lambda: 'resolved'): 'resolved',
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

    @unittest.skipUnless(mock, 'mock not installed')
    def test_mac_address(self):
        with patch('subprocess.Popen') as MockPopen:
            proc = MockPopen.return_value
            proc.communicate.return_value = (IFCONFIG, b'')
            self.assertEqual(mac_address(), 'd4:be:d9:a0:18:e1')

    def test_process_name(self):
        self.assertEqual(process_name(1), ['/sbin/init'])
        self.assertRaises(IOError, process_name, -1)
        self.assertEqual(process_name(-1, ignore_errors=True), [])

    def test_get_pid_list(self):
        self.assertIn(os.getpid(), get_pid_list())

    def test_temp_dir(self):
        with TemporaryDirectory() as tmp:
            self.assertTrue(exists(tmp))
            file = os.path.join(tmp, 'test.txt')
            input = 'test data'
            with open(file, 'w') as f:
                f.write(input)
            with open(file) as f:
                output = f.read()
            self.assertEqual(input, output)
        self.assertFalse(exists(tmp))

    def test_file_lock(self):
        with NamedTemporaryFile() as f:
            tmp = f.name
        self.assertFalse(exists(tmp))
        with file_lock(tmp):
            self.assertTrue(exists(tmp))
            with self.assertRaisesRegex(IOError, 'Could not lock'):
                with file_lock(tmp):
                    pass
        self.assertFalse(exists(tmp))

    def test_requires_commands(self):
        requires_commands('python')
        with self.assertRaisesRegex(EnforcementError, 'i_dont_exist'):
            requires_commands('i_dont_exist')

    @unittest.skipUnless(pep8, 'pep8 not installed')
    @unittest.skipUnless(mock, 'mock not installed')
    def test_pep8(self):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            style = pep8.StyleGuide(paths=[BASE_DIR], exclude=['.tox'])
            errors = style.check_files().total_errors
            msg = '%s pep8 error(s)\n%s' % (errors, mock_stdout.getvalue())
            self.assertFalse(errors, msg)

    def test_raises(self):
        self.assertTrue(raises(ValueError, int, 'not a number'))
        self.assertFalse(raises(ValueError, int, '10'))
        with self.assertRaisesRegex(ValueError, 'invalid literal'):
            self.assertTrue(raises(ImportError, int, 'not a number'))

    def test_parse_table(self):
        input = """
            ==========  ==========  ================
            name        number      boolean
            ==========  ==========  ================
            zero        0           false
            one         1           true
            two         2           true
            ==========  ==========  ================
        """

        output = [
            dict(name='zero', number='0', boolean='false'),
            dict(name='one', number='1', boolean='true'),
            dict(name='two', number='2', boolean='true'),
        ]
        self.assertEqual(parse_table(input), output)

        output = [
            dict(name='zero', number=0, boolean=False),
            dict(name='one', number=1, boolean=True),
            dict(name='two', number=2, boolean=True),
        ]
        self.assertEqual(parse_table(input, yaml=True), output)

    def test_reformat_query(self):
        class Item(object):
            name = 'Dummy'
            price = 10
            size = 'Small'

        i = Item()
        size = dict(size=i.size)
        query = "INSERT INTO items VALUES ({name}, {0.price}, {1[size]})"
        query, parameters = reformat_query(query, i, size, name=i.name)
        self.assertEqual(query, 'INSERT INTO items VALUES (?, ?, ?)')
        self.assertEqual(parameters, ('Dummy', 10, 'Small'))
