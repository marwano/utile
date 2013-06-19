#!/usr/bin/env python

import sys
from subprocess import Popen, PIPE
from utile import force_print
from testsuite.support import patch, mock, StringIO, TestCase, unittest


@patch('sys.stdout', new_callable=StringIO)
def run_force_print(mock_stdout):
    print('this output will be captured by mock')
    force_print('forced hello world')


@unittest.skipUnless(mock, 'mock not installed')
class ForcePrintTestCase(TestCase):
    def test_force_print(self):
        process = Popen(['python', __file__, 'run_force_print'], stdout=PIPE)
        output = process.communicate()[0].decode('utf8')
        self.assertEqual(output, 'forced hello world\n')
        force_print(end='')

if __name__ == '__main__' and sys.argv[-1] == 'run_force_print':
    run_force_print()
