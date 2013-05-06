# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

ACTION_ID = 'ActionID'


class AMIResponseHandler(object):

    _instance = None

    def __init__(self):
        self._callbacks = dict()

    def register_callback(self, action_id, callback):
        self._callbacks[action_id] = callback

    def handle_response(self, response):
        action_id = response[ACTION_ID]
        fn = self._callbacks.pop(action_id, None)
        if fn:
            fn(response)

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
