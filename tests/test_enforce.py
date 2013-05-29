#!/usr/bin/env python

from support import TestCase
from utile import enforce, EnforcementError, enforce_clean_exit


@enforce_clean_exit
def demo_clean_exit(x):
    enforce(x < 0, 'x must be negative')


class EnforceTestCase(TestCase):
    def setUp(self):
        self.x = 10

    def test_enforce_true(self):
        enforce(self.x > 0, 'x must be positive')

    def test_enforce_false(self):
        with self.assertRaisesRegex(EnforcementError, 'x must be negative'):
            enforce(self.x < 0, 'x must be negative')

    def test_enforce_custom_exception(self):
        with self.assertRaisesRegex(ValueError, 'x must be negative'):
            enforce(self.x < 0, 'x must be negative', ValueError)

    def test_enforce_clean_exit(self):
        with self.assertRaisesRegex(SystemExit, 'x must be negative'):
            demo_clean_exit(self.x)
