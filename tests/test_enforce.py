#!/usr/bin/env python

from unittest import TestCase
from utile import enforce, EnforcementError, enforce_clean_exit


@enforce_clean_exit
def clean_exit_test():
    x = 10
    enforce(x < 0, 'x must be negative')


class EnforceTestCase(TestCase):
    def test_enforce(self):
        x = 10
        enforce(x > 0, 'x must be positive')
        with self.assertRaisesRegexp(EnforcementError, 'x must be negative'):
            enforce(x < 0, 'x must be negative')

    def test_enforce_clean_exit(self):
        with self.assertRaisesRegexp(SystemExit, 'x must be negative'):
            clean_exit_test()
