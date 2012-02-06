import unittest
from xivo_cti.cti.commands.user_service.enable_noanswer_forward import EnableNoAnswerForward


class TestEnableNoAnswerForward(unittest.TestCase):

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "fwd",
               "value": {'destrna': '27654', 'enablerna': True}}

        enable_noanswer_forward = EnableNoAnswerForward.from_dict(msg)

        self.assertTrue(isinstance(enable_noanswer_forward, EnableNoAnswerForward))

        self.assertEquals(enable_noanswer_forward.destination, '27654')
        self.assertEquals(enable_noanswer_forward.enable, True)
