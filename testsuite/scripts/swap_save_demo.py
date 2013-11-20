#!/usr/bin/env python

from __future__ import print_function
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(dirname(abspath(__file__)))))  # path to utile
from os.path import getsize
import time
from utile import arg_parser, Arg, timed, swap_save
from threading import Thread
from Queue import Queue
from tempfile import NamedTemporaryFile
from string import ascii_letters


def normal_save(path, blocks):
    with open(path, 'w') as f:
        for i in blocks:
            f.write(i)


def poller(path, stop, sizes, delay):
    while stop.empty():
        size, first_byte = getsize(path), open(path).read(1)
        sizes.put((size, first_byte))
        time.sleep(delay / 1000.0)


def call_save(path, count, saver, file_size):
    for loop in range(count):
        blocks = [ascii_letters[loop] * 1024 for i in range(file_size * 1024)]
        with timed('saving file [%s]' % loop):
            saver(path, blocks)


def main():
    args = arg_parser(
        'Demonstrate the need for swap_save().',
        Arg('--file-size', default=10, help='Test file size in megabytes'),
        Arg('--save-count', default=10, help='Number of file saves'),
        Arg('--thread-count', default=10, help='Number of polling threads'),
        Arg('--poll-delay', default=1, help='Polling delay in ms'),
        Arg('--save-method', default='normal', choices=['normal', 'swap'],
            help='method to saving files'),
    ).parse_args()
    saver = normal_save if args.save_method == 'normal' else swap_save
    with NamedTemporaryFile(prefix='swap_save_demo_', suffix='.txt') as f:
        path = f.name
        print('test file: %s' % path)
        call_save(path, 1, saver, args.file_size)
        print('spawning threads...')
        threads = []
        stop, results = Queue(), Queue()
        for i in range(args.thread_count):
            thread = Thread(target=poller,
                            args=(path, stop, results, args.poll_delay))
            thread.start()
            threads.append(thread)
        call_save(path, args.save_count, saver, args.file_size)
        print('stopping threads...')
        stop.put('stop_threads')
        for i in threads:
            i.join()
        results = [results.get() for i in range(results.qsize())]
        print('total poll calls:', len(results))
        actual = sorted(set(results))
        size = args.file_size * 1024 * 1024
        expected = [(size, ascii_letters[i]) for i in range(args.save_count)]
        if actual == expected:
            print('unique result:', actual)
            print('TEST PASSED')
        else:
            values = [len(expected), len(actual)]
            print('Expected {} unique items found {}.'.format(*values))
            print('TEST FAILED')


if __name__ == '__main__':
    main()
