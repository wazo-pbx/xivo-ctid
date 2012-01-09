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
        self.assertEqual(cti_command.cti_connection, None)

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

    def test_get_reply(self):
        command_class = 'return_test'
        command = CTICommand({'class': command_class})
        command._command_class = command_class

        reply = command.get_reply('message', 'This is the test message', close_connection=False)

        self.assertFalse('closemenow' in reply)
        self.assertTrue('message' in reply)
        self.assertEqual(reply['message']['message'], 'This is the test message')
        self.assertEqual(reply['class'], command_class)
        self.assertFalse('replyid' in reply)

        commandid = '12345'
        command._commandid = commandid

        reply = command.get_reply('message', 'Test 2', True)

        self.assertTrue('closemenow' in reply)
        self.assertEqual(reply['replyid'], commandid)

    def test_get_warning(self):
        command_class = 'warning_test'
        command = CTICommand({'class': command_class})
        command._command_class = command_class

        reply = command.get_warning('Unknown command')

        self.assertTrue('warning' in reply)
        self.assertEqual(reply['warning']['message'], 'Unknown command')

    def test_get_message(self):
        command_class = 'message_test'
        command = CTICommand({'class': command_class})
        command._command_class = command_class

        reply = command.get_message('Test completed successfully', True)

        self.assertTrue('closemenow' in reply, 'closemenow should be present when passing close_connection -> True')
        self.assertTrue('message' in reply)
        self.assertEqual(reply['message']['message'], 'Test completed successfully')


if __name__ == "__main__":
    unittest.main()
