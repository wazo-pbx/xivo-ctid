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

from xivo_cti.tools import weak_method


class AbstractCTICommandClass(object):
    # XXX name is bad

    def __init__(self):
        self._callbacks_with_params = []

    def match_message(self, msg):
        return self._match(msg)

    def _match(self, msg):
        # should be overridden in derived class
        return True

    def from_dict(self, msg):
        command = CTICommandInstance()
        command.command_class = msg['class']
        command.commandid = msg.get('commandid')
        command.callbacks_with_params = self.callbacks_with_params
        self._parse(msg, command)
        return command

    def _parse(self, msg, command):
        # should be overriden in derived class
        pass

    def callbacks_with_params(self):
        return [callback for callback in self._callbacks_with_params if not callback[0].dead()]

    def register_callback_params(self, function, params=None):
        if not params:
            params = []
        self._callbacks_with_params.append((weak_method.WeakCallable(function), params))


class CTICommandInstance(object):
    # XXX name is bad

    pass
