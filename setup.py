
from setuptools import setup
import utile

readme = open('README.rst').read()
changes = open('CHANGES.txt').read()
version = utile.git_version(utile.__version__)

setup(
    name='utile',
    version=version,
    description="Collection of useful functions and classes",
    long_description=readme + '\n\n' + changes,
    keywords='utile',
    author='Marwan Alsabbagh',
    author_email='marwan.alsabbagh@gmail.com',
    url='https://github.com/marwano/utile',
    license='BSD',
    py_modules=['utile'],
    namespace_packages=[],
    include_package_data=True,
    test_suite='testsuite.support.suite',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
