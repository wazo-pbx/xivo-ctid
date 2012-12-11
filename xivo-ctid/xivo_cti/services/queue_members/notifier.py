# -*- coding: UTF-8 -*-


class QueueMemberNotifier(object):

    def __init__(self):
        self._callbacks_on_add = []
        self._callbacks_on_update = []
        self._callbacks_on_remove = []

    def subscribe_to_queue_member_add(self, callback):
        self._callbacks_on_add.append(callback)

    def subscribe_to_queue_member_update(self, callback):
        self._callbacks_on_update.append(callback)

    def subscribe_to_queue_member_remove(self, callback):
        self._callbacks_on_remove.append(callback)

    def _on_queue_member_added(self, queue_member):
        # XXX package private (appeler par le manager)
        self._call_callbacks(self._callbacks_on_add, queue_member)

    def _on_queue_member_updated(self, queue_member):
        # XXX package private (appeler par le manager)
        self._call_callbacks(self._callbacks_on_update, queue_member)

    def _on_queue_member_removed(self, queue_member):
        # XXX package private (appeler par le manager)
        self._call_callbacks(self._callbacks_on_remove, queue_member)

    def _call_callbacks(self, callbacks, queue_member):
        for callback in callbacks:
            callback(queue_member)
