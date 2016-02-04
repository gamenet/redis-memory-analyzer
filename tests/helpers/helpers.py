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
        self.assertEqual(total_row(data, [sum, sum, 'test']), [5, 5, 'test'])
