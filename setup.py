#!/usr/bin/env python
from rma import __version__

long_description = '''
RMA is a console tool to scan Redis key space in real time and aggregate memory usage statistic by key patterns. You may
use this tools without maintenance on production servers. You can scanning by all or selected Redis types such as "string",
"hash", "list", "set", "zset" and use matching pattern as you like. RMA try to discern key names by patterns, for example
if you have keys like 'user:100' and 'user:101' application would pick out common pattern 'user:*' in output so you can
analyze most memory distressed data in your instance.
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
    'install_requires': ['redis', 'tabulate', 'tqdm', 'msgpack-python'],
    'packages': ['rma', 'rma.helpers', 'rma.reporters', 'rma.rule', 'rma.cli'],
    'package_data': {'rma.cli': ['*.template']},
    'test_suite': 'tests.all_tests',
    'entry_points': {
        'console_scripts': [
            'rma = rma.cli.rma_cli:main',
        ],
    },
    'classifiers': [
        'Development Status :: 3 - Alpha',
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
