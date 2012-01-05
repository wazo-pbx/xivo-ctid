import unittest

from xivo_cti.cti.cti_command_factory import CTICommandFactory
from xivo_cti.cti.commands.invite_confroom import InviteConfroom


class Test(unittest.TestCase):

    def setUp(self):
        self._msg_1 = {'class': 'invite_confroom',
                       'commandid': 737000717,
                       'invitee': 'user:pcmdev/3'}

    def tearDown(self):
        pass

    def test_cti_command_factory(self):
        factory = CTICommandFactory()

        self.assertTrue(factory is not None)

    def test_get_command(self):
        factory = CTICommandFactory()

        commands = factory.get_command(self._msg_1)

        self.assertTrue(InviteConfroom in commands)

    def test_register_class(self):
        CTICommandFactory.register_class(InviteConfroom)

        self.assertTrue(InviteConfroom in CTICommandFactory._registered_classes)


if __name__ == "__main__":
    unittest.main()
