import unittest
from xivo_cti.cti.commands.user_service.enable_dnd import EnableDND


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "enablednd",
               "value": True}

        enable_dnd = EnableDND.from_dict(msg)

        self.assertTrue(isinstance(enable_dnd, EnableDND))
