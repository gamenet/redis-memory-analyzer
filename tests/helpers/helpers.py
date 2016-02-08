import unittest
from rma.helpers import *


class HelpersTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_total_row(self):
        data = [
            [1, 2, 'abc'], [4, 3, 'abc']
        ]
        self.assertEqual(make_total_row(data, [sum, sum, 'test']), [5, 5, 'test'])

    def test_pref_encoding(self):
        self.assertEqual('c [50.0%] / a [33.3%] / b [16.6%]', pref_encoding(['a', 'a', 'b', 'c', 'c', 'c']))
        self.assertEqual('c [60.0%] / aaa [40.0%]', pref_encoding(['aaa', 'aaa', 'c', 'c', 'c']))