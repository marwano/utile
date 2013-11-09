
from utile import Arg, arg_parser
from testsuite.support import StringIO, TestCase, mock, patch
import unittest
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
        return arg_parser(
            'greet someone',
            Arg('--greeting', default='hello', help='how to greet'),
            Arg('--name', default='world', help='who to greet'),
            epilog=EPILOG,
        )

    def test_defaults(self):
        actual = vars(self.get_parser().parse_args([]))
        expected = dict(greeting='hello', name='world')
        self.assertEqual(actual, expected)

    def test_arguments(self):
        actual = vars(self.get_parser().parse_args(['--name=jack']))
        expected = dict(greeting='hello', name='jack')
        self.assertEqual(actual, expected)

    def test_help(self):
        output = StringIO()
        self.get_parser().print_help(file=output)
        cleanup = re.sub(r'usage:[^\[]*\[', 'usage:  [', output.getvalue())
        self.assertEqual(normalize(cleanup), normalize(HELP))

    def test_completer(self):
        completer = lambda x: x
        parser = arg_parser('greet someone', Arg('name', completer=completer))
        action = [i for i in parser._actions if i.dest == 'name'][0]
        self.assertIs(action.completer, completer)

    @unittest.skipUnless(mock, 'mock not installed')
    def test_autocomplete_true(self):
        argcomplete = mock.Mock()
        with patch('utile.safe_import', return_value=argcomplete):
            parser = arg_parser('greet someone', autocomplete=True)
            expected = [mock.call.autocomplete(parser)]
            self.assertEqual(argcomplete.mock_calls, expected)

    @unittest.skipUnless(mock, 'mock not installed')
    def test_autocomplete_false(self):
        argcomplete = mock.Mock()
        with patch('utile.safe_import', return_value=argcomplete):
            arg_parser('greet someone', autocomplete=False)
            self.assertEqual(argcomplete.mock_calls, [])
