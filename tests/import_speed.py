#!/usr/bin/env python

import timeit

if __name__ == "__main__":
    print(timeit.timeit('import utile', number=1))
