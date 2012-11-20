# vim: set fileencoding=utf-8 :
# xivo-ctid

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class AMICallbackHandler(object):

    _instance = None

    def __init__(self):
        self._callbacks = {}

    def register_callback(self, event_name, function):
        key = event_name.lower()
        if not key in self._callbacks:
            self._callbacks[key] = list()
        self._callbacks[key].append(function)

    def unregister_callback(self, event_name, function):
        callback_key = event_name.lower()
        if callback_key in self._callbacks:
            self._callbacks[callback_key].remove(function)
            if not self._callbacks[callback_key]:
                self._callbacks.pop(callback_key)

    def get_callbacks(self, event_name):
        return self._callbacks.get(event_name.lower(), [])

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = AMICallbackHandler()
        return cls._instance
