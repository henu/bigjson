from io import BytesIO
from unittest import TestCase

import bigjson


MISSING_OPEN_QUOTE_JSON_FILE = b"""
{
    "object": {
        "x": y"
    }
}
"""

CORRUPT_BACKSLASH_ENCODING_JSON_FILE = b"""
{
    "string": "\qblah"
}
"""

MISSING_DIGIT_AFTER_DOT_JSON_FILE = b"""
{
    "number": 14.
}
"""


class TestCorruption(TestCase):

    def test_missing_open_quote(self):
        file = BytesIO(MISSING_OPEN_QUOTE_JSON_FILE)
        data = bigjson.load(file)

        with self.assertRaises(Exception) as e:
            _ = len(data)

        self.assertEqual(e.exception.args[0], "Unexpected bytes! Value 'y' Position 32")

    def test_corrupt_backslash_encoding(self):
        file = BytesIO(CORRUPT_BACKSLASH_ENCODING_JSON_FILE)
        data = bigjson.load(file)

        with self.assertRaises(Exception) as e:
            _ = len(data)

        self.assertEqual(e.exception.args[0], "Unexpected \\q in backslash encoding! Position 19")

    def test_missing_digit_after_dot(self):
        file = BytesIO(MISSING_DIGIT_AFTER_DOT_JSON_FILE)
        data = bigjson.load(file)

        with self.assertRaises(Exception) as e:
            _ = len(data)

        self.assertEqual(e.exception.args[0], "Expected digit after dot! Position 21")

