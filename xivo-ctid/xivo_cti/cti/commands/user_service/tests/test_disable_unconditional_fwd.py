import unittest
from xivo_cti.cti.commands.user_service.disable_unconditional_forward import DisableUnconditionalForward


class TestDisableUnconditionalForward(unittest.TestCase):

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "fwd",
               "value": {'destunc': '56897','enableunc': False}}

        disable_unconditional_forward = DisableUnconditionalForward.from_dict(msg)

        self.assertTrue(isinstance(disable_unconditional_forward, DisableUnconditionalForward))
        
        self.assertEquals(disable_unconditional_forward.destination,'56897')
        self.assertEquals(disable_unconditional_forward.enable,False)
