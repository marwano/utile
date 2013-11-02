#!/usr/bin/env python

import unittest
from utile import wait, wait_false, TimeoutError, safe_import
from testsuite.support import patch, mock, TestCase


@unittest.skipUnless(mock, 'mock not installed')
@patch('time.sleep')
@patch('utile.timer', side_effect=range(100))
class WaitTestCase(TestCase):
    def setUp(self):
        self.checker = mock.Mock(side_effect=[False] * 10 + [True])
        self.false_checker = mock.Mock(side_effect=[True] * 10 + [False])

    def test_success_no_timeout(self, mock_timer, mock_sleep):
        self.assertTrue(wait(callable=self.checker))

    def test_success_with_timeout(self, mock_timer, mock_sleep):
        self.assertTrue(wait(20, 0.1, self.checker))

    def test_timed_out(self, mock_timer, mock_sleep):
        self.assertRaises(TimeoutError, wait, 5, callable=self.checker)

    def test_wait_false(self, mock_timer, mock_sleep):
        self.assertFalse(wait_false(callable=self.checker))
