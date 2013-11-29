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

from xivo_dao import cel_dao

from .calls import ReceivedCall, SentCall


def answered_calls_for_phone(phone, limit):
    channels = cel_dao.channels_for_phone(phone, limit)
    answering_channels = [channel
                          for channel in channels
                          if not channel.is_caller()
                          and channel.is_answered()]
    received_calls = _convert_incoming_channels(answering_channels, limit)
    return received_calls


def missed_calls_for_phone(phone, limit):
    channels = cel_dao.channels_for_phone(phone, limit)
    missed_channels = [channel
                       for channel in channels
                       if not channel.is_caller()
                       and not channel.is_answered()]
    received_calls = _convert_incoming_channels(missed_channels, limit)
    return received_calls


def outgoing_calls_for_phone(phone, limit):
    channels = cel_dao.channels_for_phone(phone, limit)
    outgoing_channels = [channel
                         for channel in channels
                         if channel.is_caller()]
    sent_calls = _convert_outgoing_channels(outgoing_channels, limit)
    return sent_calls


def _convert_incoming_channels(incoming_channels, limit):
    received_calls = []
    for incoming_channel in incoming_channels[:limit]:
        call_id = incoming_channel.linked_id()
        caller_id = cel_dao.caller_id_by_unique_id(call_id)
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
