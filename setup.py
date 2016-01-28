#!/usr/bin/env python
import os

from rma import __version__

long_description = '''
Analyze Redis memory and show the RAM bottlenecks

Rma is a memory profiler for Redis.
'''

sdict = {
    'name': 'rma',
    'version': __version__,
    'description': 'Utilities to profile Redis RAM usage',
    'long_description': long_description,
    'url': 'https://github.com/gamenet/redis-memory-analyzer',
    'author': 'Nikolay Bondarenko',
    'author_email': 'misterionkell@gmail.com',
    'maintainer': 'Nikolay Bondarenko',
    'maintainer_email': 'misterionkell@gmail.com',
    'keywords': ['Redis', 'Memory Profiler'],
    'license': 'MIT',
    'packages': ['rma', 'rma.cli'],
    'package_data': {'rma.cli': ['*.template']},
    'test_suite': 'tests.all_tests',
    'entry_points': {
        'console_scripts': [
            'rma = rma.cli.rma:main',
        ],
    },
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)
