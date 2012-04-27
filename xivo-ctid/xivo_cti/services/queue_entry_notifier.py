from collections import defaultdict


class QueueEntryNotifier(object):

    def __init__(self):
        self._subscriptions = defaultdict(set)

    def subscribe(self, client_connection, queue_name):
        self._subscriptions[queue_name].add(client_connection)
