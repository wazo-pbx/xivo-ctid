import unittest
from xivo_cti.cti.commands.user_service.enable_busy_forward import EnableBusyForward


class TestEnableBusyForward(unittest.TestCase):

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "fwd",
               "value": {'destbusy': '1984', 'enablebusy': True}}

        enable_busy_forward = EnableBusyForward.from_dict(msg)

        self.assertTrue(isinstance(enable_busy_forward, EnableBusyForward))

        self.assertEquals(enable_busy_forward.destination, '1984')
        self.assertEquals(enable_busy_forward.enable, True)
