#!/usr/bin/env python

from __future__ import print_function
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))  # path to utile
from utile import arg_parser, Arg, ThrottleFilter, TemporaryDirectory
from timeit import timeit


def main():
    global filter
    args = arg_parser(
        'Time calls to ThrottleFilter.',
        Arg('--number', default=100, type=int, help='Number of calls to do'),
        Arg('--dir', default=None, help='Directory to save filter file'),
    ).parse_args()

    with TemporaryDirectory(dir=args.dir) as tmp:
        print('filter directory:', tmp)
        filter = ThrottleFilter(tmp, 1)
        filter.filter(None)
        duration = timeit('__main__.filter.filter(None)',
                          setup='import __main__', number=args.number)
        duration = (duration / args.number) * 10**6
        print('Average call time: %.2f microseconds' % duration)


if __name__ == '__main__':
    main()
