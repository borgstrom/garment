#!/usr/bin/env python

from setuptools import setup

import versioneer

versioneer.versionfile_source = 'garment/_version.py'
versioneer.versionfile_build = 'garment/_version.py'
versioneer.tag_prefix = '' # versions are like '1.0.4'
versioneer.parentdir_prefix = 'garment-' # dir names are like 'garment-1.0.4'

setup(name='garment',
      packages=['garment'],
      include_package_data=True,
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
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
          'fabric>=1.8,<=1.9',
          'iso8601>=0.1,<=0.2'
      ])
