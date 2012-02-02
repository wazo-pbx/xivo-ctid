import unittest
from xivo_cti.cti.commands.set_user_service import SetUserService


class TestSetUserService(unittest.TestCase):

    def test_init_from_dict(self):
        commandid = 519852486
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "enablednd",
               "value": True}

        set_user_service = SetUserService.from_dict(msg)

        self.assertEqual(set_user_service.command_class, SetUserService.COMMAND_CLASS)
        self.assertEqual(set_user_service.function, 'enablednd')
        self.assertEqual(set_user_service.value, True)
