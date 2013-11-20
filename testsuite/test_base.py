
import os
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from os.path import exists
import datetime
import os.path
import unittest
from glob import glob
from testsuite.support import (
    patch, mock, Crypto, yaml, StringIO, TestCase, int_to_byte
)
from utile import (
    safe_import, encrypt, decrypt, shell_quote, flatten, dir_dict, touch,
    process_name, process_info, get_pid_list, TemporaryDirectory, file_lock,
    requires_commands, resolve, EnforcementError, parse_table, reformat_query,
    raises, countdown, random_text, LazyResolve, swap_save, ThrottleFilter
)


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

    def test_process_name(self):
        self.assertEqual(process_name(1), ['/sbin/init'])
        self.assertRaises(IOError, process_name, -1)
        self.assertEqual(process_name(-1, ignore_errors=True), [])

    def test_process_info(self):
        info = process_info(1)
        self.assertEqual(info['Pid'], 1)
        self.assertEqual(info['PPid'], 0)
        self.assertRaises(IOError, process_info, -1)
        self.assertEqual(process_info(-1, ignore_errors=True), {})
        info = process_info()
        self.assertEqual(info['Pid'], os.getpid())
        self.assertEqual(info['PPid'], os.getppid())
        self.assertIsInstance(info['VmSize'], int)
        self.assertIsInstance(info['Name'], str)

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

    @unittest.skipUnless(mock, 'mock not installed')
    def test_countdown(self):
        with patch('utile.timer', side_effect=[0, 0, 0, 1, 1, 2, 2]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                with patch('time.sleep'):
                    countdown(2, delay=1)
        expected = 'Countdown: 2\rCountdown: 1\rCountdown: done\n'
        self.assertEqual(mock_stdout.getvalue(), expected)

    def test_random_text(self):
        a, b = random_text(10), random_text(10)
        self.assertNotEqual(a, b)
        self.assertTrue(len(a) == 10 and len(b) == 10)

    def test_raises(self):
        self.assertTrue(raises(ValueError, int, 'not a number'))
        self.assertFalse(raises(ValueError, int, '10'))
        with self.assertRaisesRegex(ValueError, 'invalid literal'):
            self.assertTrue(raises(ImportError, int, 'not a number'))

    @unittest.skipUnless(yaml, 'PyYAML not installed')
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

    def test_lazy_resolve(self):
        lazy = LazyResolve(dict(Popen='subprocess.Popen'))
        self.assertEqual(lazy.Popen, Popen)

    def test_swap_save(self):
        with NamedTemporaryFile(prefix='swap_save_') as f:
            swap_save(f.name, 'test data')
            self.assertEqual(open(f.name).read(), 'test data')
            os.remove(f.name)
            swap_save(f.name, 'test data')
            self.assertEqual(open(f.name).read(), 'test data')
            swap_save(f.name, ['test', ' data'])
            self.assertEqual(open(f.name).read(), 'test data')

    @unittest.skipUnless(mock, 'mock not installed')
    def test_throttle_filter(self):
        with TemporaryDirectory() as tmp:
            filter = ThrottleFilter(tmp, 3)
            actual = [filter.filter(None) for i in range(5)]
            self.assertEqual(actual, [1, 1, 1, 0, 0])
            os.remove(glob(tmp + os.sep + '*')[0])
            touch(tmp + os.sep + 'throttle.2000-01-01_00.000005.filter')
            self.assertEqual(filter.filter(None), 1)
            touch(tmp + os.sep + 'throttle.dummy.filter')
            with self.assertRaisesRegex(OSError, 'More then one filter found'):
                filter.filter(None)
            with patch('logging.raiseExceptions', 0):
                filter.filter(None)
