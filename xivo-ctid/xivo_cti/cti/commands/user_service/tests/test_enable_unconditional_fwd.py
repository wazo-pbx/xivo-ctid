import unittest
from xivo_cti.cti.commands.user_service.enable_unconditional_forward import EnableUnconditionalForward


class TestEnableUnconditionalForward(unittest.TestCase):

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "fwd",
               "value": {'destunc': '27654', 'enableunc': True}}

        enable_unconditional_forward = EnableUnconditionalForward.from_dict(msg)

        self.assertTrue(isinstance(enable_unconditional_forward, EnableUnconditionalForward))

        self.assertEquals(enable_unconditional_forward.destination, '27654')
        self.assertEquals(enable_unconditional_forward.enable, True)
