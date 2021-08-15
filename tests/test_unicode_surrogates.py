import os
from unittest import TestCase

import bigjson


DATA_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unicode_surrogates_data.json')


class TestUnicodeSurrogates(TestCase):

    def test_unicode_surrogates(self):

        with open(DATA_JSON_PATH, 'rb') as f:
            data = bigjson.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0], 'test\n𝄇"lol')
