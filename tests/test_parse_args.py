#!/usr/bin/env python

from unittest import TestCase, skipUnless
from utile import Arg, parse_args
from support import patch, mock
from StringIO import StringIO

EPILOG = """\
This command will greet you.
Examples:
  greet.py --greeting=hi
"""

HELP = """\
usage: [-h] [--greeting GREETING] [--name NAME]

greet someone

optional arguments:
  -h, --help           show this help message and exit
  --greeting GREETING  how to greet (default: hello)
  --name NAME          who to greet (default: world)

This command will greet you.
Examples:
greet.py --greeting=hi
"""


def normalize(text):
    return [i.strip() for i in text.strip().splitlines()]


@skipUnless(mock, 'mock not installed')
@patch('sys.stdout', new_callable=StringIO)
class ParseArgsTestCase(TestCase):
    def call_parse_args(self):
        greeting = Arg('--greeting', default='hello', help='how to greet')
        name = Arg('--name', default='world', help='who to greet')
        return parse_args('greet someone', greeting, name, epilog=EPILOG)

    def test_defaults(self, mock_stdout):
        with patch('argparse._sys.argv', new=['']):
            expected = dict(greeting='hello', name='world')
            self.assertEqual(self.call_parse_args(), expected)

    def test_arguments(self, mock_stdout):
        with patch('argparse._sys.argv', new=['', '--name=jack']):
            expected = dict(greeting='hello', name='jack')
            self.assertEqual(self.call_parse_args(), expected)

    def test_help(self, mock_stdout):
        with patch('argparse._sys.argv', new=['', '-h']):
            with self.assertRaises(SystemExit):
                self.call_parse_args()
        self.assertEqual(normalize(mock_stdout.getvalue()), normalize(HELP))
