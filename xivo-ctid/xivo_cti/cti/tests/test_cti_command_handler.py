import unittest

from xivo_cti.cti.cti_command_handler import CTICommandHandler
from xivo_cti.cti.commands.invite_confroom import InviteConfroom
from tests.mock import Mock
from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.ctiserver import CTIServer
from xivo_cti.interfaces.interface_cti import CTI


class Test(unittest.TestCase):

    def setUp(self):
        self._msg_1 = {"class": "invite_confroom",
                       "commandid": 737000717,
                       "invitee": "user:pcmdev/3"}
        self._ctiserver = Mock(CTIServer)
        self._cti_connection = CTI(self._ctiserver)

    def tearDown(self):
        pass

    def test_cti_command_handler(self):
        cti_handler = CTICommandHandler(self._cti_connection)

        self.assertTrue(cti_handler is not None)
        self.assertTrue(cti_handler._command_factory is not None)

    def test_parse_message(self):
        cti_handler = CTICommandHandler(self._cti_connection)

        self.assertEqual(len(cti_handler._commands_to_run), 0)

        cti_handler.parse_message(self._msg_1)

        self.assertEqual(len(cti_handler._commands_to_run), 1)
        command = cti_handler._commands_to_run[0]
        self.assertTrue(isinstance(command, InviteConfroom))

    def test_run_command(self):
        function = Mock()
        ret_val = {'message': 'test_return'}
        function.return_value = ret_val
        CTICommand.register_callback(function)
        cti_handler = CTICommandHandler(self._cti_connection)
        command = CTICommand({'class': 'test_function'})
        cti_handler._commands_to_run.append(command)

        ret = cti_handler.run_commands()

        self.assertTrue(ret_val in ret)
        function.assert_called_once_with(command)


if __name__ == "__main__":
    unittest.main()
