from io import BytesIO
from unittest import TestCase

import bigjson


JSON_FILE = b"""
{
    "string": "blah",
    "number": 123,
    "true": true,
    "false": false,
    "null": null,
    "array": [1, 2, 3],
    "object": {
        "x": "y"
    }
}
"""


class TestBasics(TestCase):

    def test_basics(self):
        file = BytesIO(JSON_FILE)
        data = bigjson.load(file)

        self.assertEqual(len(data), 7)
        self.assertEqual(data['string'], 'blah')
        self.assertEqual(data['number'], 123)
        self.assertEqual(data['true'], True)
        self.assertEqual(data['false'], False)
        self.assertEqual(data['null'], None)
        self.assertEqual(len(data['array']), 3)
        self.assertEqual(data['array'][0], 1)
        self.assertEqual(data['array'][1], 2)
        self.assertEqual(data['array'][2], 3)
        self.assertEqual(len(data['object']), 1)
        self.assertEqual(data['object']['x'], 'y')
