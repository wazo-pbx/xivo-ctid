import unittest

from xivo_cti.cti.cti_command_handler import CTICommandHandler


class Test(unittest.TestCase):

    def setUp(self):
        self._msg_1 = {"class": "invite-confroom",
                       "commandid": 737000717,
                       "invitee": "user:pcmdev/3"}

    def tearDown(self):
        pass

    def test_cti_command_handler(self):
        cti_handler = CTICommandHandler()

        self.assertTrue(cti_handler is not None)


if __name__ == "__main__":
    unittest.main()
