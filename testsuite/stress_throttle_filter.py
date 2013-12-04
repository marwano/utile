
from os.path import join
from utile import (arg_parser, Arg, TemporaryDirectory, ThrottleFilter,
                   parse_env, write_file)
from threading import Thread
from testsuite.support import TestCase, Queue
import logging


class SimpleFilter(object):
    def __init__(self, dir, limit):
        self.path = join(dir, 'filter.txt')
        write_file(self.path, '0')
        self.limit = limit

    def filter(self, record):
        total = int(open(self.path).read()) + 1
        write_file(self.path, str(total))
        return 1 if total <= self.limit else 0


def worker(results, filter, count):
    for i in range(count):
        try:
            results.put(filter.filter(None))
        except:
            pass


class StressThrottleFilterTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        parser = arg_parser(
            'Stress test ThrottleFilter.',
            Arg('--worker-count', default=10, type=int),
            Arg('--worker-calls', default=10, type=int),
            Arg('--debug', default=0, type=int),
        )
        args = parse_env(parser, 'utile', args=[])
        for i in ['worker_count', 'worker_calls']:
            setattr(cls, i, getattr(args, i))
        if args.debug:
            logging.basicConfig(format='%(message)s', level=logging.DEBUG)
        logging.debug('args: %s' % args)
        cls.expected = args.worker_count * args.worker_calls

    def stress(self, filter_class):
        logging.debug('')   # start a new line
        with TemporaryDirectory() as tmp:
            filter = filter_class(tmp, 0)
            threads = []
            results = Queue()
            for i in range(self.worker_count):
                thread = Thread(
                    target=worker, args=(results, filter, self.worker_calls)
                )
                thread.start()
                threads.append(thread)
            for i in threads:
                i.join()
            count = len([results.get() for i in range(results.qsize())])
            logging.debug('actual count:   {0:>5}'.format(count))
            logging.debug('expected count: {0:>5}'.format(self.expected))
            return count

    def test_throttle_filter(self):
        self.assertEqual(self.stress(ThrottleFilter), self.expected)

    def test_simple_filter(self):
        self.assertNotEqual(self.stress(SimpleFilter), self.expected)
