#!/usr/bin/env python

import sys
from unittest import TestLoader, TextTestRunner
from testsuite.support import TEST_DIR

suite = TestLoader().discover(TEST_DIR)

if __name__ == "__main__":
    TextTestRunner(verbosity=2).run(suite)
