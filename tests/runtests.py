#!/usr/bin/env python

import sys
from unittest import TestLoader, TextTestRunner
import os.path

BASE_DIR = os.path.dirname(__file__)
suite = TestLoader().discover(BASE_DIR)

if __name__ == "__main__":
    TextTestRunner(verbosity=2).run(suite)
