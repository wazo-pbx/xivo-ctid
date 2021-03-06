# -*- coding: utf-8 -*-
# Copyright 2007-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
        command.deregister_callback = self.deregister_callback
        self._parse_fun(msg, command)
        return command

    def callbacks_with_params(self):
        return list(self._callbacks_with_params)

    def deregister_callback(self, function):
        comparable_unwrapped = function
        comparable_wrapped = weak_method.WeakCallable(function)
        to_remove = [(callback, params) for callback, params in self._callbacks_with_params
                     if (callback == comparable_unwrapped or
                         callback == comparable_wrapped)]
        for pair in to_remove:
            self._callbacks_with_params.remove(pair)

    def register_callback_params(self, function, params=None):
        if not params:
            params = []
        self._callbacks_with_params.append((weak_method.WeakCallable(function), params))


class CTICommandInstance(object):

    def __str__(self):
        return getattr(self, 'command_class', 'unknown command')
