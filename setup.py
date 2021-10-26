#!/usr/bin/env python
import os
from os.path import join

base_dir = os.path.dirname(__file__)
readme_path = join(base_dir, 'README.rst')
changes = join(base_dir, 'CHANGES')

long_description = open(readme_path).read() + '\n' + open(changes).read()

__pkginfo__ = {}
with open(os.path.join(base_dir, "rma", "__pkginfo__.py")) as f:
    exec(f.read(), __pkginfo__)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='rma',
      version=__pkginfo__['version'],
      description='Utilities to profile Redis RAM usage',
      long_description=long_description,
      url='https://github.com/gamenet/redis-memory-analyzer',
      author='Nikolay Bondarenko',
      author_email='misterionkell@gmail.com',
      maintainer='Nikolay Bondarenko',
      maintainer_email='misterionkell@gmail.com',
      keywords=['Redis', 'Memory Profiler'],
      license='MIT',
      install_requires=['redis', 'tabulate', 'tqdm', 'msgpack-python>=0.4.7,<0.5.0'],
      include_package_data=True,
      packages=['rma', 'rma.helpers', 'rma.reporters', 'rma.rule', 'rma.cli'],
      python_requires='>3.5',
      package_data={
          'rma.cli': ['*.template']
      },
      test_suite='tests.all_tests',
      entry_points={
          'console_scripts': [
              'rma = rma.cli.rma_cli:main',
          ],
      },
      classifiers=__pkginfo__['classifiers'],)
