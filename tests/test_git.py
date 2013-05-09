#!/usr/bin/env python

from unittest import TestCase, skipUnless
from utile import git_version, safe_import
from support import patch, mock

PKG_INFO = """\
Metadata-Version: 1.1
Name: example-package
Version: 0.3.dev8
Summary: Example package for testing...
"""


@skipUnless(mock, 'mock not installed')
class GitTestCase(TestCase):
    def test_non_dev(self):
        for version in ['1.0a1', '1.0b2', '1.0b2.post345', '1.0c1', '1.0']:
            self.assertEqual(git_version(version), version)

    def test_git_describe(self):
        with patch('utile.which', return_value=['/usr/bin/git']):
            with patch('utile.Popen') as MockPopen:
                proc = MockPopen.return_value
                proc.communicate.return_value = ['v0.2-8-gdbc0d9c\n']
                self.assertEqual(git_version('0.3.dev'), '0.3.dev8')

    def test_pkg_info(self):
        with patch('utile.which', return_value=[]):
            with patch('os.path.exists', return_value=True):
                with patch('utile.open', create=True) as mock_open:
                    mock_open.return_value.read.return_value = PKG_INFO
                    self.assertEqual(git_version('0.3.dev'), '0.3.dev8')

    def test_no_git_or_pkg_info(self):
        with patch('utile.which', return_value=[]):
            with patch('os.path.exists', return_value=False):
                self.assertEqual(git_version('0.3.dev'), '0.3.dev')
