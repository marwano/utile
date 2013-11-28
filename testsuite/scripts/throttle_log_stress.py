#!/usr/bin/env python

from __future__ import print_function
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))  # path to utile
from utile import arg_parser, Arg, TemporaryDirectory, ThrottleFilter
from threading import Thread
from Queue import Queue
from timeit import default_timer as timer, timeit


def worker(results, filter, count, load):
    for i in range(count):
        timeit('map(str, range(10))', number=load)
        results.put(filter.filter(None))


def main():
    args = arg_parser(
        'Stress test ThrottleFilter.',
        Arg('--worker-count', default=10, type=int, help='Number of workers'),
        Arg('--worker-calls', default=100, type=int, help='calls per worker'),
        Arg('--worker-load', default=100, type=int, help='load on worker'),
    ).parse_args()
    for k, v in sorted(args.__dict__.items()):
        print('%s: %s' % (k, v))
    with TemporaryDirectory() as tmp:
        print('temporary directory: %s' % tmp)
        filter = ThrottleFilter(tmp, 0)
        threads = []
        results = Queue()
        start = timer()
        for i in range(args.worker_count):
            thread = Thread(
                target=worker,
                args=(results, filter, args.worker_calls, args.worker_load)
            )
            thread.start()
            threads.append(thread)
        for i in threads:
            i.join()
        duration = timer() - start
        actual = [results.get() for i in range(results.qsize())]
        expected = [0] * args.worker_count * args.worker_calls
        status = 'PASSED' if actual == expected else 'FAILED'
        print('test duration: %0.3fs' % duration)
        print('test status:', status)


if __name__ == '__main__':
    main()
