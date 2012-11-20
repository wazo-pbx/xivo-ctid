
import unittest
import mock

from xivo_cti.services.device.controller.aastra import AastraController
from xivo_cti import dao
from xivo_cti.dao.device_dao import DeviceDAO


class TestAastraController(unittest.TestCase):

    def setUp(self):
        dao.device = mock.Mock(DeviceDAO)

    def test_answer(self):
        device_id = 66
        peer = 'SIP/1234'

        dao.device.get_peer_name.return_value = peer

        aastra_controller = AastraController()

        result = aastra_controller.answer(device_id)

        var_content = ('Content', '<AastraIPPhoneExecute><ExecuteItem URI=\"Key:Line1\"/></AastraIPPhoneExecute>')
        var_event = ('Event', 'aastra-xml')
        var_content_type = ('Content-type', 'application/xml')

        expected_result = [peer, var_content, var_event, var_content_type]

        self.assertEqual(result, expected_result)

    def test_answer_good_peer(self):
        device_id = 66
        peer = 'SIP/abcde'

        dao.device.get_peer_name.return_value = peer

        aastra_controller = AastraController()

        result = aastra_controller.answer(device_id)

        var_content = ('Content', '<AastraIPPhoneExecute><ExecuteItem URI=\"Key:Line1\"/></AastraIPPhoneExecute>')
        var_event = ('Event', 'aastra-xml')
        var_content_type = ('Content-type', 'application/xml')

        expected_result = [peer, var_content, var_event, var_content_type]

        self.assertEqual(result, expected_result)
