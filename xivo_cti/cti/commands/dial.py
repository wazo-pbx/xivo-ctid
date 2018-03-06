# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _match(msg):
    return msg['command'] == 'dial'


def _parse(msg, command):
    command.destination = msg['destination']


Dial = CTICommandClass('ipbxcommand', _match, _parse)
Dial.add_to_registry()
