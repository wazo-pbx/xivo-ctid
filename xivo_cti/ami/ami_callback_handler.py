# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from collections import defaultdict


class AMICallbackHandler(object):

    _instance = None

    def __init__(self):
        self._callbacks = defaultdict(list)
        self._userevent_callbacks = defaultdict(list)

    def register_callback(self, event_name, function):
        key = event_name.lower()
        if function not in self._callbacks[key]:
            self._callbacks[key].append(function)

    def register_userevent_callback(self, userevent_name, function):
        key = userevent_name.lower()
        if function not in self._userevent_callbacks[key]:
            self._userevent_callbacks[key].append(function)

    def unregister_callback(self, event_name, function):
        callback_key = event_name.lower()
        if callback_key in self._callbacks:
            self._callbacks[callback_key].remove(function)
            if not self._callbacks[callback_key]:
                self._callbacks.pop(callback_key)

    def get_callbacks(self, event):
        event_name = event['Event'].lower()
        callbacks = self._callbacks.get(event_name, [])

        if event_name == 'userevent':
            key = event['UserEvent'].lower()
            callbacks = list(callbacks)
            callbacks.extend(self._userevent_callbacks.get(key, []))

        return callbacks

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = AMICallbackHandler()
        return cls._instance
