import unittest
from tests.jemalloc import JemallocTestCase
from tests.simple_splitter import SplitterTestCase
from tests.helpers.helpers import HelpersTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(JemallocTestCase))
    suite.addTest(unittest.makeSuite(SplitterTestCase))
    suite.addTest(unittest.makeSuite(HelpersTestCase))
    return suite
