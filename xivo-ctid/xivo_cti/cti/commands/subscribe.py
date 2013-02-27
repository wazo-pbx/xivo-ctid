# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_cti.cti.cti_command import CTICommandClass


def _parse(msg, command):
    command.message = msg['message']


def _parse_queue_entry_update(msg, command):
    _parse(msg, command)
    command.queue_id = int(msg['queueid'])


def _new_class(message_name, parse_fun):
    def match(msg):
        return msg['message'] == message_name

    return CTICommandClass('subscribe', match, parse_fun)


SubscribeCurrentCalls = _new_class('current_calls', _parse)
SubscribeCurrentCalls.add_to_registry()

SubscribeMeetmeUpdate = _new_class('meetme_update', _parse)
SubscribeMeetmeUpdate.add_to_registry()

SubscribeQueueEntryUpdate = _new_class('queueentryupdate', _parse_queue_entry_update)
SubscribeQueueEntryUpdate.add_to_registry()
