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


class CallNotifier(object):

    def __init__(self):
        self._callbacks = {}

    def notify(self, event):
        extension = event.extension
        if extension in self._callbacks:
            for callback in self._callbacks[extension]:
                callback(event)

    def notify_call(self, event):
        pass

    def subscribe_to_status_changes(self, extension, callback):
        self._callbacks.setdefault(extension, []).append(callback)

    def unsubscribe_from_status_changes(self, extension, callback):
        if extension in self._callbacks:
            self._callbacks[extension].remove(callback)
            if len(self._callbacks[extension]) == 0:
                self._callbacks.pop(extension)
