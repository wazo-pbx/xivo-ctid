import unittest

from xivo_cti.cti.cti_command_factory import CTICommandFactory


class Test(unittest.TestCase):

    def setUp(self):
        self._msg_1 = {'class': 'invite-confroom',
                       'commandid': 737000717,
                       'invitee': 'user:pcmdev/3'}

    def tearDown(self):
        pass

    def test_cti_command_factory(self):
        factory = CTICommandFactory()

        self.assertTrue(factory is not None)

    def test_get_command(self):
        factory = CTICommandFactory()

        command = factory.get_command(self._msg_1)

        self.assertEqual(None, command)

if __name__ == "__main__":
    unittest.main()
