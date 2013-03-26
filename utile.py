# utile.py - Collection of useful functions
# Copyright (C) 2013 Marwan Alsabbagh
# license: BSD, see LICENSE for more details.

import time
import re
import os
import itertools
from shutil import rmtree
from inspect import getargspec
from subprocess import check_output, check_call
from tempfile import mkdtemp
from contextlib import contextmanager
from fcntl import flock, LOCK_EX, LOCK_NB
from datetime import timedelta
from argparse import ArgumentParser

# list of cipher aliases http://www.openssl.org/docs/apps/enc.html
DES3, AES_128, AES_256 = 'des_ede3_cbc', 'aes_128_cbc', 'aes_256_cbc'


def save_args(obj, values):
    for i in getargspec(obj.__init__).args[1:]:
        setattr(obj, i, values[i])


def flatten(data):
    return list(itertools.chain.from_iterable(data))


def mac_address(interface='eth0'):
    output = check_output(['ifconfig', interface])
    return re.search(r'HWaddr ([\w:]+)', output).group(1)


@contextmanager
def TemporaryDirectory(suffix='', prefix='tmp', dir=None):
    path = mkdtemp(suffix, prefix, dir)
    try:
        yield path
    finally:
        rmtree(path)


@contextmanager
def file_lock(path):
    try:
        f = open(path, 'w')
        flock(f, LOCK_EX | LOCK_NB)
    except IOError:
        raise IOError("Could not lock '%s'" % path)
    try:
        yield
    finally:
        f.close()
        os.remove(path)


def shell_quote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"


def _crypt(data, **cipher_args):
    from M2Crypto.EVP import Cipher
    cipher = Cipher(**cipher_args)
    output = cipher.update(data)
    return output + cipher.final()


def encrypt(key, data, alg=AES_256):
    return _crypt(data, op=1, key=key, alg=alg, iv='', key_as_bytes=1)


def decrypt(key, data, alg=AES_256):
    return _crypt(data, op=0, key=key, alg=alg, iv='', key_as_bytes=1)


def shell(cmd, msg='', caller=check_call, shell=True, **kwargs):
    msg = msg if msg else cmd
    print ' {} '.format(msg).center(60, '-')
    start = time.time()
    returncode = caller(cmd, shell=shell, **kwargs)
    print 'duration: %s' % timedelta(seconds=time.time() - start)
    return returncode


class Arg(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def parse_args(description, *args, **kwargs):
    kwargs['description'] = description
    parser = ArgumentParser(**kwargs)
    for i in args:
        parser.add_argument(*i.args, **i.kwargs)
    return parser.parse_args()