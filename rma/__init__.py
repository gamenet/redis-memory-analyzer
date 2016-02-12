from rma.application import RmaApplication
from rma.redis import RmaRedis

__version__ = '0.1.5'
VERSION = tuple(map(int, __version__.split('.')))

__all__ = ['RmaApplication', 'RmaRedis']
