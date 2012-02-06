import unittest
from xivo_cti.cti.commands.user_service.disable_busy_forward import DisableBusyForward


class TestDiableBusyForward(unittest.TestCase):

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "fwd",
               "value": {'destbusy': '1984', 'enablebusy': False}}

        disable_busy_forward = DisableBusyForward.from_dict(msg)

        self.assertTrue(isinstance(disable_busy_forward, DisableBusyForward))

        self.assertEquals(disable_busy_forward.destination, '1984')
        self.assertEquals(disable_busy_forward.enable, False)
