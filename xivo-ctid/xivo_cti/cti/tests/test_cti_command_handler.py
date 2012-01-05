import unittest

from xivo_cti.cti.cti_command_handler import CTICommandHandler
from xivo_cti.cti.commands.invite_confroom import InviteConfroom


class Test(unittest.TestCase):

    def setUp(self):
        self._msg_1 = {"class": "invite_confroom",
                       "commandid": 737000717,
                       "invitee": "user:pcmdev/3"}

    def tearDown(self):
        pass

    def test_cti_command_handler(self):
        cti_handler = CTICommandHandler()

        self.assertTrue(cti_handler is not None)
        self.assertTrue(cti_handler._command_factory is not None)

    def test_parse_message(self):
        cti_handler = CTICommandHandler()

        self.assertTrue(cti_handler._commands_to_run.empty())

        cti_handler.parse_message(self._msg_1)

        self.assertEqual(cti_handler._commands_to_run.qsize(), 1)
        command = cti_handler._commands_to_run.get(False)
        self.assertTrue(isinstance(command, InviteConfroom))


if __name__ == "__main__":
    unittest.main()
