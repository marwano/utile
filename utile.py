# utile.py - Collection of useful functions
# Copyright (C) 2013 Marwan Alsabbagh
# license: BSD, see LICENSE for more details.

__version__ = '0.3.dev'

import time
import re
import os
import os.path
import sys
import itertools
import logging.config
from timeit import default_timer as timer
from functools import wraps
from shutil import rmtree
from hashlib import sha256
from inspect import getargspec
from subprocess import check_output, check_call, Popen, PIPE
from tempfile import mkdtemp
from contextlib import contextmanager
from fcntl import flock, LOCK_EX, LOCK_NB
from datetime import timedelta, datetime
from importlib import import_module
from argparse import (
    ArgumentParser, ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter)

# Alias for easier importing
now = datetime.now


def resolve(name):
    item, module = None, []
    for i in name.split('.'):
        module.append(i)
        try:
            item = getattr(item, i)
        except AttributeError:
            item = import_module('.'.join(module))
    return item


def safe_import(name, default=None):
    try:
        return resolve(name)
    except ImportError:
        return default


etree = safe_import('lxml.etree')
AES = safe_import('Crypto.Cipher.AES')
bunch_or_dict = safe_import('bunch.Bunch', dict)


def dir_dict(obj, default=None):
    names = [i for i in dir(obj) if not i.startswith('_')]
    return {i: getattr(obj, i, default) for i in names}


def pretty_xml(xml):
    enforce(etree, 'lxml is not installed.')
    root = etree.fromstring(xml, etree.XMLParser(remove_blank_text=True))
    return etree.tostring(root, pretty_print=True)


def element_to_dict(elem, return_tuple=False):
    children = bunch_or_dict(element_to_dict(i, True) for i in elem)
    if return_tuple:
        return elem.tag, children or elem.text
    else:
        return children


def xml_to_dict(xml, *args, **kwargs):
    enforce(etree, 'lxml is not installed.')
    root = etree.fromstring(xml, etree.XMLParser(*args, **kwargs))
    return element_to_dict(root)


def git_version(version):
    if 'dev' not in version:
        return version
    git_details = ''
    if which('git'):
        cmd = ['git', 'describe']
        git_details = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()[0]
    if git_details:
        return version + git_details.split('-')[1]
    elif os.path.exists('PKG-INFO'):
        info = open('PKG-INFO').read()
        return re.findall(r'^Version: (.*)$', info, re.MULTILINE)[0]
    else:
        return version


def save_args(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        names = getargspec(f).args[1:]
        defaults = zip(reversed(names), reversed(getargspec(f).defaults))
        items = zip(names, args) + kwargs.items() + defaults
        for k, v in items:
            if not hasattr(self, k):
                setattr(self, k, v)
        return f(self, *args, **kwargs)
    return wrapper


def flatten(data):
    return list(itertools.chain.from_iterable(data))


def process_name(pid=None):
    pid = pid or os.getpid()
    cmdline = open('/proc/%s/cmdline' % pid).read()
    return cmdline.strip('\x00').split('\x00')


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
        raise IOError('Could not lock %r' % path)
    try:
        yield
    finally:
        f.close()
        os.remove(path)


def shell_quote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"


def _cipher(key):
    enforce(AES, 'pycrypto is not installed.')
    return AES.new(sha256(key).digest(), AES.MODE_CFB, '\x00' * AES.block_size)


def encrypt(key, data):
    return _cipher(key).encrypt(data)


def decrypt(key, data):
    return _cipher(key).decrypt(data)


class EnforcementError(Exception):
    pass


def enforce(rule, msg, exception=EnforcementError):
    if not rule:
        raise exception(msg)


def enforce_clean_exit(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        try:
            return func(*args, **kwds)
        except EnforcementError as err:
            sys.exit('ERROR: %s' % err)
    return wrapper


def which(cmd):
    os_paths = os.environ['PATH'].split(os.pathsep)
    cmd_paths = [os.path.join(i, cmd) for i in os_paths]
    return [i for i in cmd_paths if os.path.exists(i)]


def commands_required(commands):
    missing = [cmd for cmd in commands.split() if not which(cmd)]
    enforce(not missing, '%r command(s) not found' % ' '.join(missing))


def shell(cmd=None, msg=None, caller=check_call, strict=False, **kwargs):
    msg = msg if msg else cmd
    kwargs.setdefault('shell', True)
    if kwargs['shell']:
        kwargs.setdefault('executable', '/bin/bash')
    if strict:
        if not kwargs['shell'] or not isinstance(cmd, basestring):
            msg = 'strict can only be used when shell=True and cmd is a string'
            raise ValueError(msg)
        cmd = 'set -e;' + cmd
    print(' {} '.format(msg).center(60, '-'))
    start = timer()
    returncode = caller(cmd, **kwargs)
    print('duration: %s' % timedelta(seconds=timer() - start))
    return returncode


class TimeoutError(Exception):
    pass


def wait(check, timeout=None, delay=0.1):
    start = timer()
    while not check():
        duration = timer() - start
        if timeout and duration > timeout:
            raise TimeoutError('waited for %0.3fs' % duration)
        time.sleep(delay)


class ArgDefaultRawHelpFormatter(
        ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter):
    """Help message formatter which adds default values to argument help and
    which retains any formatting in descriptions.
    """


class Arg(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def parse_args(description, *args, **kwargs):
    kwargs['description'] = description
    kwargs.setdefault('formatter_class', ArgDefaultRawHelpFormatter)
    parser = ArgumentParser(**kwargs)
    for i in args:
        parser.add_argument(*i.args, **i.kwargs)
    return bunch_or_dict(parser.parse_args().__dict__)
