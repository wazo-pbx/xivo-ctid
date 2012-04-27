import unittest

from mock import Mock

from xivo_cti.services.queue_entry_notifier import QueueEntryNotifier
from xivo_cti.interfaces.interface_cti import CTI

QUEUE_NAME_1 = 'testqueue'
QUEUE_NAME_2 = 'anothertestqueue'


class TestQueueEntryNotifier(unittest.TestCase):

    def setUp(self):
        self.notifier = QueueEntryNotifier()

    def test_subscribe(self):
        connection_1 = Mock(CTI)
        connection_2 = Mock(CTI)

        self.notifier.subscribe(connection_1, QUEUE_NAME_1)
        self.notifier.subscribe(connection_2, QUEUE_NAME_2)

        subscriptions = self.notifier._subscriptions[QUEUE_NAME_1]

        self.assertTrue(connection_1 in subscriptions)
        self.assertTrue(connection_2 not in subscriptions)

        subscriptions_2 = self.notifier._subscriptions[QUEUE_NAME_2]

        self.assertTrue(connection_2 in subscriptions_2)

    def test_publish(self):
        pass
