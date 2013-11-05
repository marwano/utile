#!/usr/bin/env python

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))  # path to utile.py
from utile import arg_parser, Arg, force_print
from testsuite.support import patch, StringIO


@patch('sys.stdout', new_callable=StringIO)
def call_force_print(text, end, mock_stdout):
    print('This should never get printed.')
    force_print(text, end=end)


def main():
    args = arg_parser(
        'Command used to test force_print().',
        Arg('--text', default=''),
        Arg('--end', default='\n')
    ).parse_args()
    call_force_print(args.text, args.end)

if __name__ == '__main__':
    main()
