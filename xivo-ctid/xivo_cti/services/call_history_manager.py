# -*- coding: UTF-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2011  Avencall
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

from collections import namedtuple
from xivo_cti.dao.celdao import CELDAO


ReceivedCall = namedtuple('ReceivedCall', ['date', 'duration', 'caller_name'])


SentCall = namedtuple('SentCall', ['date', 'duration', 'extension'])


class CallHistoryMgr(object):
    def __init__(self, cel_dao):
        self._cel_dao = cel_dao

    def answered_calls_for_phone(self, phone, limit):
        channels = self._cel_dao.channels_for_phone(phone)
        answering_channels = [channel
                              for channel in channels
                              if not channel.is_caller()
                              and channel.is_answered()]
        received_calls = self._convert_incoming_channels(answering_channels, limit)
        return received_calls

    def missed_calls_for_phone(self, phone, limit):
        channels = self._cel_dao.channels_for_phone(phone)
        missed_channels = [channel
                              for channel in channels
                              if not channel.is_caller()
                              and not channel.is_answered()]
        received_calls = self._convert_incoming_channels(missed_channels, limit)
        return received_calls

    def outgoing_calls_for_phone(self, phone, limit):
        channels = self._cel_dao.channels_for_phone(phone)
        outgoing_channels = [channel
                           for channel in channels
                           if channel.is_caller()]
        sent_calls = self._convert_outgoing_channels(outgoing_channels, limit)
        return sent_calls

    def _convert_incoming_channels(self, incoming_channels, limit):
        received_calls = []
        for incoming_channel in incoming_channels[:limit]:
            call_id = incoming_channel.linked_id()
            caller_id = self._cel_dao.caller_id_by_unique_id(call_id)
            received_call = ReceivedCall(incoming_channel.channel_start_time(),
                                         incoming_channel.answer_duration(),
                                         caller_id)
            received_calls.append(received_call)
        return received_calls

    def _convert_outgoing_channels(self, outgoing_channels, limit):
        sent_calls = []
        for outgoing_channel in outgoing_channels[:limit]:
            sent_call = SentCall(outgoing_channel.channel_start_time(),
                                 outgoing_channel.answer_duration(),
                                 outgoing_channel.exten())
            sent_calls.append(sent_call)
        return sent_calls


    @classmethod
    def new_from_uri(cls, uri):
        return cls(CELDAO.new_from_uri(uri))
