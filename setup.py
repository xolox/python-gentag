#!/usr/bin/env python

# Simple and powerful tagging for Python objects.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: March 4, 2018
# URL: https://github.com/xolox/python-gentag

"""Setup script for the `gentag` package."""

# Standard library modules.
import codecs
import os
import re

# De-facto standard solution for Python packaging.
from setuptools import setup, find_packages


def get_readme():
    """Get the contents of the ``README.rst`` file as a Unicode string."""
    with codecs.open(get_absolute_path('README.rst'), 'r', 'utf-8') as handle:
        return handle.read()


def get_version(*args):
    """Get the package's version (by extracting it from the source code)."""
    module_path = get_absolute_path(*args)
    with open(module_path) as handle:
        for line in handle:
            match = re.match(r'^__version__\s*=\s*["\']([^"\']+)["\']$', line)
            if match:
                return match.group(1)
    raise Exception("Failed to extract version from %s!" % module_path)


def get_requirements(*args):
    """Get requirements from pip requirement files."""
    requirements = set()
    with open(get_absolute_path(*args)) as handle:
        for line in handle:
            # Strip comments.
            line = re.sub(r'^#.*|\s#.*', '', line)
            # Ignore empty lines
            if line and not line.isspace():
                requirements.add(re.sub(r'\s+', '', line))
    return sorted(requirements)


def get_absolute_path(*args):
    """Transform relative pathnames into absolute pathnames."""
    directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directory, *args)


setup(name='gentag',
      version=get_version('gentag', '__init__.py'),
      description='Simple and powerful tagging for Python objects.',
      long_description=get_readme(),
      url='https://github.com/xolox/python-gentag',
      author='Peter Odding',
      author_email='peter@peterodding.com',
      packages=find_packages(),
      install_requires=get_requirements('requirements.txt'),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing',
          'Topic :: Text Processing :: Indexing',
      ])
