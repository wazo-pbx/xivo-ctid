import unittest
from xivo_cti.cti.commands.user_service.disable_dnd import DisableDND


class TestDisableDND(unittest.TestCase):

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "enablednd",
               "value": False}

        disable_dnd = DisableDND.from_dict(msg)

        self.assertTrue(isinstance(disable_dnd, DisableDND))
