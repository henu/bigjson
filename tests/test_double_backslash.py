from io import BytesIO
from unittest import TestCase

import bigjson


JSON_FILE = b"""
{
    "1": "single \\\\ backslash",
    "2": "double \\\\\\\\ backslash",
    "3": "triple \\\\\\\\\\\\ backslash"
}
"""


class TestDoubleBackslash(TestCase):

    def test_double_backslash(self):
        file = BytesIO(JSON_FILE)
        data = bigjson.load(file)

        self.assertEqual(len(data), 3)
        self.assertEqual(data['1'], 'single \\ backslash')
        self.assertEqual(data['2'], 'double \\\\ backslash')
        self.assertEqual(data['3'], 'triple \\\\\\ backslash')
