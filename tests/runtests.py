#!/usr/bin/env python

import sys
from unittest import TestLoader, TextTestRunner
from support import BASE_DIR


suite = TestLoader().discover(BASE_DIR)


if __name__ == "__main__":
    TextTestRunner(verbosity=2).run(suite)
