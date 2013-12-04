
import time
from os.path import getsize
from utile import arg_parser, Arg, swap_save, write_file, parse_env
from threading import Thread, Event
from tempfile import NamedTemporaryFile
from string import ascii_letters
from testsuite.support import TestCase, Queue
import logging


def worker(path, stop, sizes, delay):
    while not stop.is_set():
        sizes.put((getsize(path), open(path).read(1)))
        time.sleep(delay / 1000.0)
    sizes.put((getsize(path), open(path).read(1)))


class StressSwapSaveTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        parser = arg_parser(
            'Stress test swap_save.',
            Arg('--file-size', default=1, type=int),
            Arg('--save-count', default=10, type=int),
            Arg('--worker-count', default=10, type=int),
            Arg('--poll-delay', default=1, type=int),
            Arg('--debug', default=0, type=int),
        )
        args = parse_env(parser, 'utile', args=[])
        for i in ['file_size', 'save_count', 'worker_count', 'poll_delay']:
            setattr(cls, i, getattr(args, i))
        if args.debug:
            logging.basicConfig(format='%(message)s', level=logging.DEBUG)
        logging.debug('args: %s' % args)
        size = cls.file_size * 1024 * 1024
        cls.expected = [(size, i) for i in ascii_letters[0:cls.save_count]]

    def blocks(self, position):
        for i in range(self.file_size * 1024):
            yield ascii_letters[position] * 1024

    def stress(self, save_func):
        logging.debug('')   # start a new line
        with NamedTemporaryFile(prefix='stress_swap_save_') as f:
            write_file(f.name, self.blocks(0))
            threads = []
            stop, results = Event(), Queue()
            logging.debug('spawning threads...')
            for i in range(self.worker_count):
                thread = Thread(
                    target=worker,
                    args=(f.name, stop, results, self.poll_delay)
                )
                thread.start()
                threads.append(thread)
            for i in range(self.save_count):
                logging.debug('saving file [%s]' % i)
                save_func(f.name, self.blocks(i))
            logging.debug('stopping threads...')
            stop.set()
            for i in threads:
                i.join()
            results = [results.get() for i in range(results.qsize())]
            actual = sorted(set(results))
            logging.debug('total polls: %s' % len(results))
            logging.debug('actual unique:   {0:>5}'.format(len(actual)))
            logging.debug('expected cunique:{0:>5}'.format(len(self.expected)))
            return actual

    def test_swap_save(self):
        self.assertEqual(self.stress(swap_save), self.expected)

    def test_write_file(self):
        self.assertNotEqual(self.stress(write_file), self.expected)
