#!/usr/bin/env python

import os
from os.path import exists
from unittest import TestCase, skipUnless
from tempfile import NamedTemporaryFile
from utile import shell
from subprocess import CalledProcessError
from StringIO import StringIO
from support import patch, mock


@skipUnless(mock, 'mock not installed')
@skipUnless(exists('/bin/echo'), '/bin/echo not found')
@patch('sys.stdout', new_callable=StringIO)
class ShellTestCase(TestCase):
    def setUp(self):
        f = NamedTemporaryFile()
        f.close()
        self.tmp = f.name
        self.hello = '/bin/echo hello > %s' % self.tmp
        self.many = (
            'invalid_command 2> {0};'
            '/bin/echo hello >> {0}'.format(self.tmp)
        )

    def tearDown(self):
        if exists(self.tmp):
            os.remove(self.tmp)

    def test_basic(self, mock_stdout):
        self.assertEqual(shell(self.hello), 0)
        self.assertEqual(open(self.tmp).read(), 'hello\n')

    def test_many_commands_without_strict(self, mock_stdout):
        self.assertEqual(shell(self.many), 0)
        self.assertIn('hello\n', open(self.tmp).read())

    def test_many_commands_with_strict(self, mock_stdout):
        with self.assertRaises(CalledProcessError):
            shell(self.many, strict=True)

    def test_invalid_strict_call(self, mock_stdout):
        with self.assertRaises(ValueError):
            shell(self.many, strict=True, shell=False)
