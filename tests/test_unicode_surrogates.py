import os
from unittest import TestCase

import bigjson


SURROGATES_PATH = os.path.join(os.path.dirname(
                               os.path.abspath(__file__)),
                               "unicode_surrogates_data.json")
ZHCN_PATH = os.path.join(os.path.dirname(
                         os.path.abspath(__file__)), "unicode_zhcn.json")


class TestUnicodeSurrogates(TestCase):

    def test_unicode_surrogates_rb(self):
        with open(SURROGATES_PATH, "rb") as f:
            data = bigjson.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0], "test\n𝄇\"lol")
            self.assertEqual(data[1],
                             "Caretaker\u00e2\u20ac\u2122s accommodation")
        with open(ZHCN_PATH, "rb") as zhf:
            data = bigjson.load(zhf)
            self.assertEqual(data["name"], "金牌综艺")
            self.assertEqual(data["languages"][0]["name"], "Chinese")

    def test_unicode_surrogates_r(self):
        with open(SURROGATES_PATH, "r") as f:
            data = bigjson.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0], "test\n𝄇\"lol")
            self.assertEqual(data[1],
                             "Caretaker\u00e2\u20ac\u2122s accommodation")
        with open(ZHCN_PATH, "r") as zhf:
            data = bigjson.load(zhf)
            self.assertEqual(data["name"], "金牌综艺")
            self.assertEqual(data["languages"][0]["name"], "Chinese")

