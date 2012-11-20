import unittest
from xivo_cti.ctiserver import CTIServer


class TestCTIServer(unittest.TestCase):

    def test_send_cti_event(self):
        event = {'event': 'My test event'}
        server = CTIServer()

        server.send_cti_event(event)

        self.assertTrue(server._cti_events.qsize() > 0)
        result = server._cti_events.get()

        self.assertEqual(result, event)
