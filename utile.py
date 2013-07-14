# utile.py - Collection of useful functions
# Copyright (C) 2013 Marwan Alsabbagh
# license: BSD, see LICENSE for more details.

from __future__ import print_function
import time
import re
import os
import os.path
import sys
import string
from itertools import chain
from timeit import default_timer as timer
from functools import wraps
from shutil import rmtree
from hashlib import sha256
from tempfile import mkdtemp
from contextlib import contextmanager
from fcntl import flock, LOCK_EX, LOCK_NB
from datetime import timedelta, datetime
from textwrap import dedent
from operator import itemgetter


__version__ = '0.4.dev'
PY3 = sys.version_info[0] == 3
string_types = str if PY3 else basestring


def resolve(obj):
    if callable(obj):
        return obj()
    item, module = None, []
    for i in obj.split('.'):
        module.append(i)
        try:
            item = getattr(item, i)
        except AttributeError:
            top_module = __import__('.'.join(module))
            if item:
                item = getattr(item, i)
            else:
                item = top_module
    return item


class LazyResolve(object):
    def __init__(self, lookup=None):
        self.lookup = lookup or dict()

    def __getattr__(self, name):
        obj = resolve(self.lookup.get(name, name))
        setattr(self, name, obj)
        return obj


def safe_import(name, default=None):
    try:
        return resolve(name)
    except ImportError:
        return default


def force_print(*args, **kwargs):
    print(*args, file=sys.__stdout__, **kwargs)


def bunch_or_dict(*args, **kwargs):
    _class = safe_import('bunch.Bunch', dict)
    return _class(*args, **kwargs)


def dir_dict(obj, default=None, only_public=True):
    names = dir(obj)
    if only_public:
        names = [i for i in names if not i.startswith('_')]
    return bunch_or_dict((i, getattr(obj, i, default)) for i in names)


def requires_package(name, pypi_name=None):
    pypi_name = pypi_name or name.split('.')[0]
    msg = 'Could not import %r. Install it by running:\npip install %s'
    enforce(safe_import(name), msg % (name, pypi_name))
    return safe_import(name)


def requires_commands(commands):
    missing = [i for i in commands.split() if not which(i)]
    enforce(not missing, '%r command(s) not found' % ' '.join(missing))


def pretty_xml(xml):
    etree = requires_package('lxml.etree')
    root = etree.fromstring(xml, etree.XMLParser(remove_blank_text=True))
    return etree.tostring(root, pretty_print=True, encoding='unicode')


def element_to_dict(elem, return_tuple=False):
    children = bunch_or_dict(element_to_dict(i, True) for i in elem)
    if return_tuple:
        return elem.tag, children or elem.text
    else:
        return children


def xml_to_dict(xml, *args, **kwargs):
    etree = requires_package('lxml.etree')
    root = etree.fromstring(xml, etree.XMLParser(*args, **kwargs))
    return element_to_dict(root)


def slicer_by_size(sizes):
    s = [slice(sum(sizes[0:i]), sum(sizes[0:i+1])) for i in range(len(sizes))]
    return itemgetter(*s)


def parse_table(text, yaml=False):
    if yaml:
        decoder = requires_package('yaml').load
    else:
        decoder = lambda x: x
    lines = dedent(text).strip().splitlines()
    slicer = slicer_by_size([len(i) for i in re.findall('=+ *', lines[0])])
    keys = [i.strip() for i in slicer(lines[1])]
    rows = []
    for line in lines[3:-1]:
        values = [decoder(i.strip()) for i in slicer(line)]
        rows.append(bunch_or_dict(zip(keys, values)))
    return rows


def git_version(version):
    from subprocess import Popen, PIPE
    if 'dev' not in version:
        return version
    describe = ''
    if which('git'):
        process = Popen(['git', 'describe'], stdout=PIPE, stderr=PIPE)
        describe, _ = process.communicate()
    if describe:
        return version + describe.decode('utf8').split('-')[1]
    elif os.path.exists('PKG-INFO'):
        info = open('PKG-INFO').read()
        return re.findall(r'^Version: (.*)$', info, re.MULTILINE)[0]
    else:
        return version


def save_args(f):
    from inspect import getargspec

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        names = getargspec(f).args[1:]
        defaults = zip(reversed(names), reversed(getargspec(f).defaults))
        positional = zip(names, args)
        keyword = kwargs.items()
        for k, v in chain(defaults, positional, keyword):
            setattr(self, k, v)
        return f(self, *args, **kwargs)
    return wrapper


def flatten(data):
    return list(chain.from_iterable(data))


def process_name(pid=None):
    pid = pid or os.getpid()
    with open('/proc/%s/cmdline' % pid) as f:
        return f.read().strip('\x00').split('\x00')


def mac_address(interface='eth0'):
    from subprocess import Popen, PIPE
    output, _ = Popen(['ifconfig', interface], stdout=PIPE).communicate()
    return re.search(r'HWaddr ([\w:]+)', output.decode('utf8')).group(1)


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
        f.close()
        raise IOError('Could not lock %r' % path)
    try:
        yield
    finally:
        f.close()
        os.remove(path)


def shell_quote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"


def _cipher(key):
    AES = requires_package('Crypto.Cipher.AES', 'pycrypto')
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


def shell(cmd=None, msg=None, caller=None, strict=False, **kwargs):
    from subprocess import check_call
    caller = caller or check_call
    msg = msg if msg else cmd
    kwargs.setdefault('shell', True)
    if kwargs['shell']:
        kwargs.setdefault('executable', '/bin/bash')
    if strict:
        if not kwargs['shell'] or not isinstance(cmd, string_types):
            msg = 'strict can only be used when shell=True and cmd is a string'
            raise ValueError(msg)
        cmd = 'set -e;' + cmd
    print(' {0} '.format(msg).center(60, '-'))
    start = timer()
    returncode = caller(cmd, **kwargs)
    print('duration: %s' % timedelta(seconds=timer() - start))
    return returncode


class TimeoutError(Exception):
    pass


def wait(timeout=None, delay=0.1, callable=None, *args, **kwargs):
    start = timer()
    while True:
        result = callable(*args, **kwargs)
        if result:
            return result
        duration = timer() - start
        if timeout and duration > timeout:
            raise TimeoutError('waited for %0.3fs' % duration)
        time.sleep(delay)


def reformat_query(query, *args, **kwargs):
    f = string.Formatter()
    parsed = list(f.parse(query))
    query = '?'.join([i[0] for i in parsed])
    fields = [i[1] for i in parsed if i[1] is not None]
    parameters = tuple(f.get_field(i, args, kwargs)[0] for i in fields)
    return query, parameters


class Arg(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def arg_parser(description, *args, **kwargs):
    from argparse import ArgumentParser
    kwargs['description'] = description
    kwargs.setdefault('formatter_class', formatter.UtileArgFormatter)
    parser = ArgumentParser(**kwargs)
    for i in args:
        parser.add_argument(*i.args, **i.kwargs)
    return parser


def _lazy_define_arg_formatter():
    import argparse

    class UtileArgFormatter(argparse.ArgumentDefaultsHelpFormatter,
                            argparse.RawDescriptionHelpFormatter):
        """
        Help message formatter which adds default values to argument help and
        which retains any formatting in descriptions.
        """

    return UtileArgFormatter


formatter = LazyResolve(dict(UtileArgFormatter=_lazy_define_arg_formatter))
