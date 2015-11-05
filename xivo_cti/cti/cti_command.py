# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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
from xivo_cti.cti import cti_command_registry


class CTICommandClass(object):

    def __init__(self, class_name, match_fun, parse_fun):
        if match_fun is None:
            match_fun = self._default_match
        if parse_fun is None:
            parse_fun = self._default_parse
        self.class_name = class_name
        self._match_fun = match_fun
        self._parse_fun = parse_fun
        self._callbacks_with_params = []

    @staticmethod
    def _default_match(msg):
        return True

    @staticmethod
    def _default_parse(msg, command):
        pass

    def add_to_registry(self):
        cti_command_registry.register_class(self)

    def add_to_getlist_registry(self, function_name):
        cti_command_registry.register_getlist_class(self, function_name)

    def match_message(self, msg):
        return self._match_fun(msg)

    def from_dict(self, msg):
        command = CTICommandInstance()
        command.command_class = msg['class']
        command.commandid = msg.get('commandid')
        command.callbacks_with_params = self.callbacks_with_params
        self._parse_fun(msg, command)
        return command

    def callbacks_with_params(self):
        return [callback for callback in self._callbacks_with_params if not callback[0].dead()]

    def deregister_callback(self, function):
        comparable = weak_method.WeakCallable(function)
        to_remove = []
        for fn, params in self._callbacks_with_params:
            if comparable == fn:
                to_remove.append((fn, params))
        for pair in to_remove:
            self._callbacks_with_params.remove(pair)

    def register_callback_params(self, function, params=None):
        if not params:
            params = []
        self._callbacks_with_params.append((weak_method.WeakCallable(function), params))


class CTICommandInstance(object):

    pass
