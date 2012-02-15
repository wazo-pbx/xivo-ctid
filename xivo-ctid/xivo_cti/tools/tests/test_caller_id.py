import unittest

from xivo_cti.tools.caller_id import build_caller_id, _complete_caller_id


class TestCallerID(unittest.TestCase):

    def test_caller_id_no_num(self):
        begin = '"User One"'
        name = 'User One'
        number = '123'

        caller_id = build_caller_id(begin, name, number)

        self.assertEqual(caller_id, '"%s" <%s>' % (name, number))

    def test_caller_id_number(self):
        begin = '"User One" <123>'
        name = 'User One'
        number = '123'

        caller_id = build_caller_id(begin, name, number)

        self.assertEqual(caller_id, '"%s" <%s>' % (name, number))

    def test_complete_caller_id(self):
        cid = '"User One" <1234>'

        self.assertTrue(_complete_caller_id(cid))
