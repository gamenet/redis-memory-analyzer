import unittest
from rma.jemalloc import Jemalloc


class JemallocTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_align(self):
        data = [[79, 80], [253, 256], [512, 512], [513, 768], [3645, 3840], [4098, 8192], [4200304, 8388608]]
        for given, expected in data:
            self.assertEqual(Jemalloc.align(given), expected)
