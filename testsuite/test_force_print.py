
import unittest
from subprocess import Popen, PIPE
from os.path import join
from testsuite.support import mock, TestCase, TEST_DIR


@unittest.skipUnless(mock, 'mock not installed')
class ForcePrintTestCase(TestCase):
    def test_force_print(self):
        force_print = join(TEST_DIR, 'force_print.py')
        process = Popen(['python', force_print, '--text=hello'], stdout=PIPE)
        output = process.communicate()[0].decode('utf8')
        self.assertEqual(output, 'hello\n')
