# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
