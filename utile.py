# utile.py - Collection of useful functions
# Copyright (C) 2013 Marwan Alsabbagh
# license: BSD, see LICENSE for more details.

__version__ = '0.2a0'

import time
import re
import os
import sys
import itertools
from shutil import rmtree
from hashlib import sha256
from inspect import getargspec
from subprocess import check_output, check_call
from tempfile import mkdtemp
from contextlib import contextmanager
from fcntl import flock, LOCK_EX, LOCK_NB
from datetime import timedelta, datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter

DEB_REQUIRES_MSG = """
The package(s) '{missing}' are currently not installed. You can install them by typing:
sudo apt-get install {missing}
""".strip()

# an alias for easier importing
now = datetime.now


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


def cipher(key):
    from Crypto.Cipher import AES
    return AES.new(sha256(key).digest(), AES.MODE_CBC, '\x00' * AES.block_size)


def encrypt(key, data):
    return cipher(key).encrypt(data)


def decrypt(key, data):
    return cipher(key).decrypt(data)


def deb_packages():
    lines = check_output(['dpkg', '--get-selections']).splitlines()
    lines = [i.split() for i in lines]
    return [i[0] for i in lines if i[1] == 'install']


def deb_requires(needed):
    missing = set(needed.split()).difference(deb_packages())
    if missing:
        print(DEB_REQUIRES_MSG.format(missing=' '.join(missing)))
        sys.exit(1)


def shell(cmd=None, msg=None, caller=check_call, shell=True, strict=False, **kwargs):
    msg = msg if msg else cmd
    if strict:
        if not shell or not isinstance(cmd, basestring):
            raise ValueError('strict can only be used when shell=True and cmd is a string')
        cmd = 'set -e;' + cmd
    print ' {} '.format(msg).center(60, '-')
    start = time.time()
    returncode = caller(cmd, shell=shell, **kwargs)
    print 'duration: %s' % timedelta(seconds=time.time() - start)
    return returncode


class ArgDefaultRawDescrHelpFormatter(ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter):
    """Help message formatter which adds default values to argument help and
    which retains any formatting in descriptions.
    """


class Arg(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def parse_args(description, *args, **kwargs):
    from bunch import Bunch
    kwargs['description'] = description
    kwargs.setdefault('formatter_class', ArgDefaultRawDescrHelpFormatter)
    parser = ArgumentParser(**kwargs)
    for i in args:
        parser.add_argument(*i.args, **i.kwargs)
    return Bunch(parser.parse_args().__dict__)
