# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

ACTION_ID = 'ActionID'


class AMIResponseHandler(object):

    _instance = None

    def __init__(self):
        self._callbacks = dict()

    def register_callback(self, action_id, callback):
        self._callbacks[action_id] = callback

    def handle_response(self, response):
        action_id = response.get(ACTION_ID)
        fn = self._callbacks.pop(action_id, None)
        if fn:
            fn(response)

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
