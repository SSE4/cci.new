#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(name='cci.new',
      version='1.0',
      description='cci.new command',
      author='SSE4',
      author_email='tomskside@gmail.com',
      packages=find_packages(exclude=['tests']),
      entry_points={'console_scripts': ['cci.new=cci.new:main']}
     )
