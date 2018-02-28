# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


class CallNotifier(object):
    def __init__(self, pubsub):
        self._pubsub = pubsub

    def notify(self, event):
        self._pubsub.publish(('calls_outgoing', event.source), event)
        self._pubsub.publish(('calls_incoming', event.destination), event)

    def subscribe_to_incoming_call_events(self, extension, callback):
        self._pubsub.subscribe(('calls_incoming', extension), callback)

    def subscribe_to_outgoing_call_events(self, extension, callback):
        self._pubsub.subscribe(('calls_outgoing', extension), callback)

    def unsubscribe_from_incoming_call_events(self, extension, callback):
        self._pubsub.unsubscribe(('calls_incoming', extension), callback)

    def unsubscribe_from_outgoing_call_events(self, extension, callback):
        self._pubsub.unsubscribe(('calls_outgoing', extension), callback)
