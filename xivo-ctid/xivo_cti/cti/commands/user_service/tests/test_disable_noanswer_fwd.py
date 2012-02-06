import unittest
from xivo_cti.cti.commands.user_service.disable_noanswer_forward import DisableNoAnswerForward


class TestDisableNoAnswerForward(unittest.TestCase):

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "fwd",
               "value": {'destrna': '27654', 'enablerna': False}}

        disable_noanswer_forward = DisableNoAnswerForward.from_dict(msg)

        self.assertTrue(isinstance(disable_noanswer_forward, DisableNoAnswerForward))

        self.assertEquals(disable_noanswer_forward.destination, '27654')
        self.assertEquals(disable_noanswer_forward.enable, False)
