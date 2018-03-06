# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _match(msg):
    return msg['command'] == 'queueadd'


def _parse(msg, command):
    command.member = msg.get('member')
    command.queue = msg.get('queue')


QueueAdd = CTICommandClass('ipbxcommand', _match, _parse)
QueueAdd.add_to_registry()
