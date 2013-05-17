#!/usr/bin/env python

from unittest import TestCase
from utile import Arg, ParseArgs
from StringIO import StringIO
import re

EPILOG = """\
This command will greet you.
Examples:
  greet.py --greeting=hi
"""

HELP = """\
usage:  [-h] [--greeting GREETING] [--name NAME]

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


class ParseArgsTestCase(TestCase):
    def get_parser(self):
        greeting = Arg('--greeting', default='hello', help='how to greet')
        name = Arg('--name', default='world', help='who to greet')
        return ParseArgs('greet someone', greeting, name, epilog=EPILOG)

    def test_defaults(self):
        expected = dict(greeting='hello', name='world')
        self.assertEqual(self.get_parser().parse([]), expected)

    def test_arguments(self):
        expected = dict(greeting='hello', name='jack')
        self.assertEqual(self.get_parser().parse(['--name=jack']), expected)

    def test_help(self):
        output = StringIO()
        self.get_parser().parser.print_help(file=output)
        cleanup = re.sub('usage: [^\s]*', 'usage: ', output.getvalue())
        self.assertEqual(normalize(cleanup), normalize(HELP))
