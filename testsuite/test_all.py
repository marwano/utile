#!/usr/bin/env python

from testsuite.support import TEST_DIR, unittest

suite = unittest.TestLoader().discover(TEST_DIR)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite)
