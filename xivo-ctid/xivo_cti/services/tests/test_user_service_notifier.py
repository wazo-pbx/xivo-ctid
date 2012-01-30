import unittest
from xivo_cti.services.user_service_notifier import UserServiceNotifier

import Queue


class TestUserServiceNotifier(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dnd_enabled(self):
        user_id = 34
        ipbx_id = 'xivo_test'
        notifier = UserServiceNotifier()
        notifier.events_cti = Queue.Queue()
        notifier.ipbx_id = ipbx_id
        expected = {"class": "getlist",
                    "config": {"enablednd": True},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": ipbx_id}

        notifier.dnd_enabled(user_id)

        self.assertTrue(notifier.events_cti.qsize() > 0)
        event = notifier.events_cti.get()
        self.assertEqual(event, expected)
