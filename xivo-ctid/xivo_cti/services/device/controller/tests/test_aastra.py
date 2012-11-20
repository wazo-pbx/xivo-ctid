import unittest

from mock import patch

from xivo_cti.services.device.controller.aastra import AastraController


class TestAastraController(unittest.TestCase):

    @patch('xivo_dao.device_dao.get_peer_name')
    def test_answer(self, mock_get_peer_name):
        device_id = 66
        peer = 'SIP/1234'

        mock_get_peer_name.return_value = peer

        aastra_controller = AastraController()

        result = aastra_controller.answer(device_id)

        var_content = ('Content', '<AastraIPPhoneExecute><ExecuteItem URI=\"Key:Line1\"/></AastraIPPhoneExecute>')
        var_event = ('Event', 'aastra-xml')
        var_content_type = ('Content-type', 'application/xml')

        expected_result = [peer, var_content, var_event, var_content_type]

        self.assertEqual(result, expected_result)

    @patch('xivo_dao.device_dao.get_peer_name')
    def test_answer_good_peer(self, mock_get_peer_name):
        device_id = 66
        peer = 'SIP/abcde'

        mock_get_peer_name.return_value = peer

        aastra_controller = AastraController()

        result = aastra_controller.answer(device_id)

        var_content = ('Content', '<AastraIPPhoneExecute><ExecuteItem URI=\"Key:Line1\"/></AastraIPPhoneExecute>')
        var_event = ('Event', 'aastra-xml')
        var_content_type = ('Content-type', 'application/xml')

        expected_result = [peer, var_content, var_event, var_content_type]

        self.assertEqual(result, expected_result)
