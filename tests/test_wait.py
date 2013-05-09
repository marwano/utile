#!/usr/bin/env python

from unittest import TestCase, skipUnless
from utile import wait, TimeoutError, safe_import
from support import patch, mock


@skipUnless(mock, 'mock not installed')
@patch('time.sleep')
@patch('utile.timer', side_effect=range(100))
class WaitTestCase(TestCase):
    def setUp(self):
        self.checker = mock.Mock(side_effect=[False] * 10 + [True])

    def test_success_no_timeout(self, mock_timer, mock_sleep):
        self.assertIsNone(wait(self.checker))

    def test_success_with_timeout(self, mock_timer, mock_sleep):
        self.assertIsNone(wait(self.checker, 20))

    def test_timed_out(self, mock_timer, mock_sleep):
        self.assertRaises(TimeoutError, wait, self.checker, 5)
