import unittest

from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.missing_field_exception import MissingFieldException
from tests.mock import Mock


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

        self.assertEqual(len(CTICommand.required_fields), 1)

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

    def test_match_message(self):
        self.assertFalse(CTICommand.match_message({}))

        CTICommand.conditions = [('class', 'test_command'), ('value', 'to_match')]
        self.assertTrue(CTICommand.match_message({'class': 'test_command', 'value': 'to_match'}))
        self.assertTrue(CTICommand.match_message({'class': 'test_command', 'value': 'to_match', 'other': 'not_checked'}))
        self.assertFalse(CTICommand.match_message({'class': 'test_command'}))

    def test_register_callback(self):
        command = CTICommand({'class': 'callback_test'})

        self.assertEqual(command.callbacks, [])

        function = Mock()
        CTICommand.register_callback(function)

        self.assertTrue(function in CTICommand._callbacks)

        command = CTICommand({'class': 'callback_test'})
        self.assertTrue(function in command.callbacks)
        self.assertEqual(len(command.callbacks), 1)


if __name__ == "__main__":
    unittest.main()
