#!/usr/bin/env python

from setuptools import setup

setup(name='garment',
      packages=['garment'],
      include_package_data=True,
      version='0.1',
      license="Apache License, Version 2.0",
      description='A collection of fabric tasks that roll up into a single deploy function. The whole process is coordinated through a single deployment configuration file named deploy.conf',
      long_description=open('README.rst').read(),
      author='Evan Borgstrom',
      author_email='evan@fatbox.ca',
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
          'fabric>=1.8,<=1.9'
      ])
