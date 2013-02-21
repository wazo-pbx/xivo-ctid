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
from xivo_cti.exception import MissingFieldException


class CTICommand(object):

    CLASS = 'class'
    COMMANDID = 'commandid'
    REPLYID = 'replyid'

    required_fields = [CLASS]
    _callbacks_with_params = []

    def __init__(self):
        self._msg = None
        self.cti_connection = None
        self.command_class = None
        self.commandid = None

    def callbacks_with_params(self):
        return [callback for callback in self._callbacks_with_params if not callback[0].dead()]

    def _init_from_dict(self, msg):
        self._msg = msg
        self._check_required_fields()
        self.commandid = self._msg.get(self.COMMANDID)
        self.command_class = self._msg[self.CLASS]

    def _check_required_fields(self):
        for field in self.required_fields:
            if field not in self._msg:
                raise MissingFieldException(u'Missing %s in CTI command' % field)

    def get_reply(self, message_type, message, close_connection=False):
        rep = {'class': self.command_class,
               message_type: message}
        if self.commandid:
            rep['replyid'] = self.commandid
        if close_connection:
            rep['closemenow'] = True
        return rep

    def get_warning(self, message, close_connection=False):
        return self.get_reply('warning', message, close_connection)

    def get_message(self, message, close_connection=False):
        return self.get_reply('message', message, close_connection)

    def user_id(self):
        if self.cti_connection and 'userid' in self.cti_connection.connection_details:
            return self.cti_connection.connection_details['userid']

    @classmethod
    def match_message(cls, message):
        for field, value in cls.conditions:
            try:
                if isinstance(field, tuple):
                    (field1, subfield) = field
                    message_field = message[field1][subfield]
                else:
                    message_field = message[field]
                if not message_field == value:
                    return False
            except KeyError:
                return False
        return True

    @classmethod
    def register_callback_params(cls, function, params=None):
        if not params:
            params = []
        cls._callbacks_with_params.append((weak_method.WeakCallable(function), params))

    @classmethod
    def from_dict(cls, msg):
        instance = cls()
        instance._init_from_dict(msg)
        return instance
