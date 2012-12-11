
import unittest
from xivo_cti.ctiserver import CTIServer
from mock import Mock
from xivo_cti.cti_config import Config


class TestCTIServer(unittest.TestCase):

    def test_send_cti_event(self):
        event = {'event': 'My test event'}
        server = CTIServer(Mock(Config))

        server.send_cti_event(event)

        self.assertTrue(server._cti_events.qsize() > 0)
        result = server._cti_events.get()

        self.assertEqual(result, event)
