# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import namedtuple
from xivo_dao import celdao


ReceivedCall = namedtuple('ReceivedCall', ['date', 'duration', 'caller_name'])
SentCall = namedtuple('SentCall', ['date', 'duration', 'extension'])


def answered_calls_for_phone(phone, limit):
    channels = celdao.channels_for_phone(phone, limit)
    answering_channels = [channel
                          for channel in channels
                          if not channel.is_caller()
                          and channel.is_answered()]
    received_calls = _convert_incoming_channels(answering_channels, limit)
    return received_calls


def missed_calls_for_phone(phone, limit):
    channels = celdao.channels_for_phone(phone, limit)
    missed_channels = [channel
                       for channel in channels
                       if not channel.is_caller()
                       and not channel.is_answered()]
    received_calls = _convert_incoming_channels(missed_channels, limit)
    return received_calls


def outgoing_calls_for_phone(phone, limit):
    channels = celdao.channels_for_phone(phone, limit)
    outgoing_channels = [channel
                         for channel in channels
                         if channel.is_caller()]
    sent_calls = _convert_outgoing_channels(outgoing_channels, limit)
    return sent_calls


def _convert_incoming_channels(incoming_channels, limit):
    received_calls = []
    for incoming_channel in incoming_channels[:limit]:
        call_id = incoming_channel.linked_id()
        caller_id = celdao.caller_id_by_unique_id(call_id)
        received_call = ReceivedCall(incoming_channel.channel_start_time(),
                                     incoming_channel.answer_duration(),
                                     caller_id)
        received_calls.append(received_call)
    return received_calls


def _convert_outgoing_channels(outgoing_channels, limit):
    sent_calls = []
    for outgoing_channel in outgoing_channels[:limit]:
        sent_call = SentCall(outgoing_channel.channel_start_time(),
                             outgoing_channel.answer_duration(),
                             outgoing_channel.exten())
        sent_calls.append(sent_call)
    return sent_calls
