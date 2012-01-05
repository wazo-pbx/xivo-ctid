import unittest

from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.missing_field_exception import MissingFieldException


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cti_command(self):
        command_class = u'test_command'
        cti_command = CTICommand({'class': command_class})

        self.assertEqual(cti_command._commandid, None)
        self.assertEqual(cti_command._command_class, command_class)

        commandid = '12345'
        cti_command = CTICommand({'class': command_class, 'commandid': commandid})

        self.assertEqual(cti_command._commandid, commandid)
        self.assertEqual(cti_command._command_class, command_class)

        self.assertEqual(len(CTICommand._required_fields), 1)

    def test_required_fields(self):
        try:
            CTICommand({})
            self.assertTrue(False, u'Should raise an exception')
        except MissingFieldException:
            self.assertTrue(True, u'Should raise an exception')

        try:
            command_class = u'test_command'
            CTICommand({'class': command_class})
            self.assertTrue(True, u'Should not raise an exception')
        except MissingFieldException:
            self.assertTrue(False, u'Should raise an exception')


if __name__ == "__main__":
    unittest.main()
