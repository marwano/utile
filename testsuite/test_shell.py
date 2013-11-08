
import unittest
from os.path import exists
from tempfile import NamedTemporaryFile
from utile import shell
from subprocess import CalledProcessError
from testsuite.support import patch, mock, StringIO, read_file, TestCase


@unittest.skipUnless(mock, 'mock not installed')
@unittest.skipUnless(exists('/bin/echo'), '/bin/echo not found')
@unittest.skipUnless(exists('/bin/bash'), '/bin/bash not found')
@patch('sys.stdout', new_callable=StringIO)
class ShellTestCase(TestCase):
    hello = '/bin/echo hello'
    invalid = 'invalid_command;/bin/echo hello'

    def test_basic(self, mock_stdout):
        with NamedTemporaryFile() as out:
            self.assertEqual(shell(self.hello, stdout=out), 0)
            self.assertEqual(read_file(out.name), 'hello\n')

    def test_verbose(self, mock_stdout):
        with NamedTemporaryFile() as out, NamedTemporaryFile() as err:
            shell(self.hello, stdout=out, stderr=err, verbose=True)
            self.assertEqual(read_file(err.name).strip(), self.hello)

    def test_verbose_with_strict(self, mock_stdout):
        with NamedTemporaryFile() as out, NamedTemporaryFile() as err:
            shell(self.hello, stdout=out, stderr=err, verbose=True,
                  strict=True)
            self.assertEqual(read_file(err.name).strip(), self.hello)

    def test_many_commands_without_strict(self, mock_stdout):
        with NamedTemporaryFile() as out, NamedTemporaryFile() as err:
            self.assertEqual(shell(self.invalid, stdout=out, stderr=err), 0)
            self.assertEqual(read_file(out.name), 'hello\n')
            self.assertIn('command not found', read_file(err.name))

    def test_many_commands_with_strict(self, mock_stdout):
        with NamedTemporaryFile() as out, NamedTemporaryFile() as err:
            with self.assertRaises(CalledProcessError):
                shell(self.invalid, stdout=out, stderr=err, strict=True)

    def test_strict_call_with_value_error(self, mock_stdout):
        with self.assertRaises(ValueError):
            shell(self.invalid, strict=True, shell=False)
