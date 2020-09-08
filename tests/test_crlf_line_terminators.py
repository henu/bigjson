from unittest import TestCase

import os

import bigjson


DATA_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crlf_data.json')


class TestCrlfLineTerminators(TestCase):

    def test_crlf_line_terminators(self):

        file_in = open(DATA_JSON_PATH, 'rb')
        json_obj = bigjson.load(file_in, encoding='utf-8')

        self.assertEqual(len(json_obj['nested_list1']), 2)
        self.assertEqual(len(json_obj['nested_list1'][0]['sub_nested_arr1']), 2)
        self.assertEqual(json_obj['nested_list1'][0]['sub_nested_arr1'][0]['ssn_1'], 'v1')
