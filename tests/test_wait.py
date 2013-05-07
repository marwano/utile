#!/usr/bin/env python

from unittest import TestCase, skipUnless
from utile import wait, TimeoutError, safe_import
patch = safe_import('mock.patch')
Mock = safe_import('mock.Mock')


@skipUnless(Mock, 'mock not installed')
class WaitTestCase(TestCase):
    def setUp(self):
        self.patch_sleep = patch('time.sleep')
        self.patch_time = patch('utile.default_timer', side_effect=range(100))
        self.patch_time.start()
        self.patch_sleep.start()
        self.checker = Mock(side_effect=[False] * 10 + [True])

    def tearDown(self):
        self.patch_time.stop()
        self.patch_sleep.stop()

    def test_success_no_timeout(self):
        self.assertIsNone(wait(self.checker))

    def test_success_with_timeout(self):
        self.assertIsNone(wait(self.checker, 20))

    def test_timed_out(self):
        self.assertRaises(TimeoutError, wait, self.checker, 5)
