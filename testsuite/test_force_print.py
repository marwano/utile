#!/usr/bin/env python

import sys
from unittest import TestCase, skipUnless
from subprocess import check_output
from utile import force_print
from testsuite.support import patch, mock, StringIO


@patch('sys.stdout', new_callable=StringIO)
def run_force_print(mock_stdout):
    print('this output will be captured by mock')
    force_print('forced hello world')


@skipUnless(mock, 'mock not installed')
class ForcePrintTestCase(TestCase):
    def test_force_print(self):
        output = check_output(['python', __file__, 'run_force_print'])
        self.assertEqual(output.decode('utf8'), 'forced hello world\n')
        force_print(end='')

if __name__ == '__main__' and sys.argv[-1] == 'run_force_print':
    run_force_print()
