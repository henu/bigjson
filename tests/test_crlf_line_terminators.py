import os
from unittest import TestCase

import bigjson


DATA_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crlf_data.json')


def _load_data(self, mode):
    if mode == "r":
        file_in =  open(DATA_JSON_PATH, mode, encoding="utf-8")
    else:
        file_in =  open(DATA_JSON_PATH, mode)

    json_obj = bigjson.load(file_in, encoding='utf-8')
    file_in.close()
    return json_obj


class TestCrlfLineTerminators(TestCase):

    def test_crlf_line_terminators_rb(self):
        json_obj = _load_data(self, "rb")
        self.assertEqual(len(json_obj['nested_list1']), 2)
        self.assertEqual(len(json_obj['nested_list1'][0]['sub_nested_arr1']), 2)
        self.assertEqual(json_obj['nested_list1'][0]['sub_nested_arr1'][0]['ssn_1'], 'v1')

    def test_crlf_line_terminators_r(self):
        json_obj = _load_data(self, "r")
        self.assertEqual(len(json_obj['nested_list1']), 2)
        self.assertEqual(len(json_obj['nested_list1'][0]['sub_nested_arr1']), 2)
        self.assertEqual(json_obj['nested_list1'][0]['sub_nested_arr1'][0]['ssn_1'], 'v1')
