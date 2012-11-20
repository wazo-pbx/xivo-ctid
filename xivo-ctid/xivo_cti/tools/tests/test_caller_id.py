import unittest

from xivo_cti.tools.caller_id import build_caller_id, _complete_caller_id, extract_number


class TestCallerID(unittest.TestCase):

    def test_caller_id_no_num(self):
        begin = '"User One"'
        name = 'User One'
        number = '123'

        cid_all, cid_name, cid_number = build_caller_id(begin, name, number)

        self.assertEqual(cid_all, '"%s" <%s>' % (name, number))
        self.assertEqual(cid_name, name)
        self.assertEqual(cid_number, number)

    def test_caller_id_number(self):
        begin = '"User One" <123>'
        name = 'User One'
        number = '123'

        cid_all, cid_name, cid_number = build_caller_id(begin, name, number)

        self.assertEqual(cid_all, '"%s" <%s>' % (name, number))
        self.assertEqual(cid_name, name)
        self.assertEqual(cid_number, number)

    def test_complete_caller_id(self):
        cid = '"User One" <1234>'

        self.assertTrue(_complete_caller_id(cid))

    def test_extract_number(self):
        caller_id = '"User 1" <1001>'

        ret = extract_number(caller_id)

        self.assertEqual(ret, '1001')

    def test_extract_number_not_a_caller_id(self):
        self.assertRaises(ValueError, extract_number, '1001')
