# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


class EndpointNotifier(object):

    def __init__(self, pubsub):
        self._pubsub = pubsub

    def notify(self, event):
        extension = event.extension
        self._pubsub.publish(('status', extension), event)

    def subscribe_to_status_changes(self, extension, callback):
        self._pubsub.subscribe(('status', extension), callback)

    def unsubscribe_from_status_changes(self, extension, callback):
        self._pubsub.unsubscribe(('status', extension), callback)
