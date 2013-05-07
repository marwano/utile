#!/usr/bin/env python

from unittest import TestCase
from utile import enforce, EnforcementError, enforce_clean_exit


@enforce_clean_exit
def clean_exit_test(x):
    enforce(x < 0, 'x must be negative')


class EnforceTestCase(TestCase):
    def setUp(self):
        self.x = 10

    def test_enforce_true(self):
        enforce(self.x > 0, 'x must be positive')

    def test_enforce_false(self):
        with self.assertRaisesRegexp(EnforcementError, 'x must be negative'):
            enforce(self.x < 0, 'x must be negative')

    def test_enforce_custom_exception(self):
        with self.assertRaisesRegexp(ValueError, 'x must be negative'):
            enforce(self.x < 0, 'x must be negative', ValueError)

    def test_enforce_clean_exit(self):
        with self.assertRaisesRegexp(SystemExit, 'x must be negative'):
            clean_exit_test(self.x)
