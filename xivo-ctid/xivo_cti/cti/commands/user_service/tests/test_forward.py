import unittest
from xivo_cti.cti.commands.user_service.set_forward import SetForward


class TestSetForward(unittest.TestCase):

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "fwd",
               "value": {'destname': '27654', 'enablename': True}}



        set_forward = SetForward.from_dict(msg)


        self.assertEquals(set_forward.destination, '27654')
        self.assertEquals(set_forward.enable, True)
