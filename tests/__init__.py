import unittest
from tests.jemalloc import JemallocTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(JemallocTestCase))
    return suite
