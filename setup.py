#!/usr/bin/env python

from setuptools import setup

import re

# load our version from our init file
init_data = open('garment/__init__.py').read()
matches = re.search(r"__version__ = '([^']+)'", init_data, re.M)
if matches:
    version = matches.group(1)
else:
    raise RuntimeError("Unable to load version")

setup(name='garment',
      packages=['garment'],
      include_package_data=True,
      version=version,
      license="Apache License, Version 2.0",
      description='A collection of fabric tasks that roll up into a single deploy function. The whole process is coordinated through a single deployment configuration file named deploy.conf',
      long_description=open('README.rst').read(),
      author='Evan Borgstrom',
      author_email='evan@borgstrom.ca',
      url='https://github.com/fatbox/garment',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: English',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      install_requires=[
          'setuptools',
          'PyYAML',
          'fabric>=1.8,<=1.9',
          'iso8601>=0.1,<=0.2'
      ])
