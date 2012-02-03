import unittest
from xivo_cti.cti.commands.user_service.enable_filter import EnableFilter


class TestEnableFilter(unittest.TestCase):

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "incallfilter",
               "value": True}

        enable_filter = EnableFilter.from_dict(msg)

        self.assertTrue(isinstance(enable_filter, EnableFilter))
