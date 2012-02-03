import unittest
from xivo_cti.cti.commands.user_service.disable_filter import DisableFilter


class TestDisableFilter(unittest.TestCase):

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "incallfilter",
               "value": False}

        disable_filter = DisableFilter.from_dict(msg)

        self.assertTrue(isinstance(disable_filter, DisableFilter))
