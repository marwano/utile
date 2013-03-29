import os
import re
from setuptools import setup

README = open('README.rst').read()
CHANGES = open('CHANGES.txt').read()
VERSION = re.findall("__version__ = '(.*)'", open('utile.py').read())[0]

setup(
    name='utile',
    version=VERSION,
    description="Collection of useful functions and classes",
    long_description=README + '\n\n' + CHANGES,
    keywords='utile',
    author='Marwan Alsabbagh',
    author_email='marwan.alsabbagh@gmail.com',
    url='https://github.com/marwano/utile',
    license='BSD',
    py_modules=['utile'],
    namespace_packages=[],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
